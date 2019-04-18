import os
import maya
import click
import time
from collections import namedtuple
from fabric import Connection, Config
from invoke.exceptions import UnexpectedExit
from tao.settings import GITLAB_READ_TOKEN


_DB_HOST = os.getenv('DB_HOST', '10.1.2.17')
_DB_PREFIX = os.getenv('DB_PREFIX', 'ctu_tao')
_DB_USER = 'ctu'
_DB_ADMIN_USER = 'root'
_DB_ADMIN_PASSWORD = 'ScTu31*'
_DOCKER_USER = 'ci'
_DOCKER_PASSWORD = 'CciPci123'
_DOCKER_REGISTRY = os.getenv('DOCKER_REGISTRY', 'harbor.dx-corp.top')

_SQL_COMPONENT = 'ctu-sql'
_SQL_REPO = 'https://dev.dingxiang-inc.com:2020/api/v4/projects/608'

_JMX_PORT_MAP = {
    'ctu-console': 17777,
    'ctu-engine': 17090,
    'ctu-indictator': 13100,
    'indicator-center': 13101,
    'monitor-agent': 14000,
    'ctu-constantid': 18090,
    'ctu-constantid-service': 19527}
_JMX_PARAM = '-Djava.rmi.server.hostname=%(host)s -Dcom.sun.management.jmxremote -Dcom.sun.management.jmxremote.port=%(port)s -Dcom.sun.management.jmxremote.authenticate=false -Dcom.sun.management.jmxremote.ssl=false'


def _validate_app(ctx, param, value):
    apps = []
    AppDeploy = namedtuple('AppDeploy', ('name', 'image', 'version'))
    for app in value:
        if ':' not in app or app[0] == ':' or app[-1] == ':':
            raise click.BadParameter('app should be format like <name>:<version>')
        image, version = app.split(':', 1)
        if '/' in image:
            name = image.rsplit('/', 1)[1]
        else:
            name = image
            image = _DOCKER_REGISTRY + '/ctu-group/' + name
        apps.append(AppDeploy(name, image, version))
    return apps


@click.command('deploy_docker', context_settings={
    'ignore_unknown_options': True,
    'allow_extra_args': True})
@click.option('--host', '-h', required=True, help='host to deploy')
@click.option('--user', '-u', default='root', help='user name of SSH login, default is root')
@click.option('--password', '-p', default='dingxiang-inc@2018', help='password of SSH login')
@click.option('--version', '-v', default='', help='version to deploy, used in sql init')
@click.option('--resetdb', '-r', is_flag=True, help='if set, will reset database')
@click.option('--resetconf', '-f', is_flag=True, help='if set, will reset configuration')
@click.option('--component', '-c', multiple=True, required=True, callback=_validate_app, help='component to deploy, format: <name>:<version>')
def deploy(host, user, password, version, resetdb, resetconf, component):
    ''' deploy services to specified machine via fabric
        example:
        python3 -m tao.tools deploy_docker -h 10.1.2.13 -p dx@666 -c console-ui:master -c console:master
        python3 -m tao.tools deploy_docker -h 10.1.2.13 -p dx@666 -c harbor.dx-corp.top/ctu-group/ctu-console-ui:master
    '''
    config = Config(overrides={'sudo': {'password': password}})
    sql_component = [c for c in component if c.name == _SQL_COMPONENT]
    if sql_component:
        sql_version = sql_component[0].version
    else:
        sql_version = version or 'master'
    _echo("sql_version: %s" % sql_version)
    component = [c for c in component if c.name != _SQL_COMPONENT]
    if not component:
        _echo("no components to deploy")
        raise RuntimeError
    with Connection(host, user, config=config, connect_kwargs={'password': password}) as conn:
        conn.version = version
        conn.reset_db = resetdb
        conn.reset_conf = resetconf
        conn.run('test -e docker || mkdir docker')  # create docker directory
        all_containers = conn.run('docker ps -a')
        container_names = [e.split()[-1] for e in all_containers.stdout.splitlines()[1:]]
        _echo('login to harbor')
        _docker_login(conn)
        if conn.reset_db:
            _echo('init mysql database')
            _init_mysql(conn, sql_version)
            _echo('init license file')
            _init_license(conn)
        _echo('init zookeeper')
        if 'zookeeper' in container_names:
            _echo('"zookeeper" is already running!')
        else:
            conn.run('docker run --name zookeeper --restart always --network host --log-opt max-size=256m -d harbor.dx-corp.top/basic/zookeeper:3.4.10')
            time.sleep(5)
        component.sort(key=_sort_component)
        for app_item in component:
            _echo('start to deploy %s:%s' % (app_item.image, app_item.version))
            _do_deploy(conn, app_item, container_names)
        if 'jmxmon' not in container_names:
            _echo('jmxmon not running, start it!')
            conn.run('docker run --rm -d --network host --name jmxmon harbor.dx-corp.top/aladdin/jmxmon:0.0.2')
        _echo('sleep 5s and show running containers')
        time.sleep(5)
        conn.run('docker ps')


def _sort_component(c):
    return c.name == 'ctu-engine'  # ctu-engine should be the last one


def _docker_login(conn):
    conn.run('docker login -u %s -p %s %s' % (
        _DOCKER_USER, _DOCKER_PASSWORD, _DOCKER_REGISTRY))


def _init_mysql(conn, sql_version):
    db_name = _get_db_name(_DB_PREFIX, conn.host, conn.version)
    for file_name in ('mysql-dump.sql', 'mysql-init.sql'):
        _echo('fetch "%s"' % file_name)
        curl_cmd = 'curl -sNH "PRIVATE-TOKEN: %s" "%s/repository/files/%s/raw?ref=%s" -o mysql-dump.sql' % (GITLAB_READ_TOKEN, _SQL_REPO, file_name, sql_version)
        result = conn.run(curl_cmd)
        if '{"message":"404 ' not in result.stdout:
            _echo('%s fetched' % file_name)
            break
        _echo('file "%s" not found!' % file_name)
    conn.run('docker run --rm arey/mysql-client -h %s -u %s -p%s -e "CREATE DATABASE IF NOT EXISTS %s; GRANT ALL PRIVILEGES ON %s.* TO \'%s\'@\'%%\';"' % (
        _DB_HOST, _DB_ADMIN_USER, _DB_ADMIN_PASSWORD, db_name, db_name, _DB_USER))
    conn.run('docker run --rm -v $PWD/mysql-dump.sql:/sql/mysql-dump.sql arey/mysql-client -h %s -u %s -p%s -D %s -e "source /sql/mysql-dump.sql"' % (
        _DB_HOST, _DB_ADMIN_USER, _DB_ADMIN_PASSWORD, db_name))


def _init_license(conn):
    db_name = _get_db_name(_DB_PREFIX, conn.host, conn.version)
    conn.run('curl -sNH "PRIVATE-TOKEN: %s" "%s/repository/files/license.sql/raw?ref=master" -o license.sql' % (GITLAB_READ_TOKEN, _SQL_REPO))
    conn.run('docker run --rm -v $HOME/license.sql:/sql/license.sql arey/mysql-client -h %s -u %s -p%s -D %s -e "source /sql/license.sql"' % (
        _DB_HOST, _DB_ADMIN_USER, _DB_ADMIN_PASSWORD, db_name))


def _do_deploy(conn, app, container_names):
    _echo('pull image of "%s" from docker registry' % app.name)
    img_path = app.image + ':' + app.version
    conn.run('docker pull ' + img_path)
    if app.name in container_names:
        _echo('stop and remove container "%s"' % app.name)
        conn.run('docker rm -f ' + app.name)
    with conn.cd('docker'):
        conn.run('test -e %(name)s || mkdir %(name)s' % {'name': app.name})
        _update_conf(conn, app, img_path)
        _start_app(conn, app, img_path)


def _update_nginx_conf_and_config_json(conn, container_id):
    conn.run('docker cp %s:/usr/local/nginx/conf/nginx.conf nginx.conf || docker cp %s:/etc/nginx/nginx.conf nginx.conf' % (container_id, container_id))
    conn.run("sed -i -E 's/[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+/%s/g' nginx.conf" % conn.host)  # noqa: W605
    conn.run('docker cp %s:/usr/local/nginx/html/config.json config.json || docker cp %s:/usr/share/nginx/html/config.json config.json' % (container_id, container_id))
    conn.run("sed -i -E 's/.*\"version\".*/    \"version\": \"%s\"/g' config.json" % conn.version)
    conn.run("sed -i -E '/isTestEnv/d' config.json")  # remove isTestEnv flag


def _get_db_name(prefix, host, version):
    if not version:
        return prefix
    db_name = '%s_%s_' % (prefix, host.replace('.', '_'))
    if len(db_name) + len(version) >= 64:  # db_name should < 64
        return db_name + version[8:(64 - len(db_name))].lower().replace('.', '_').replace('-', '_')

    return '%s_%s_%s' % (prefix, host.replace('.', '_'), version.lower().replace('.', '_').replace('-', '_'))


def _update_application_properties(conn, container_id):
    db_name = _get_db_name(_DB_PREFIX, conn.host, conn.version)
    conn.run('docker cp %s:/home/admin/application.properties application.properties' % container_id)
    conn.run("sed -i -E 's/^logHome=.+/logHome=\.\/logs/g' application.properties")  # noqa: W605
    conn.run("sed -i -E 's/^spring.datasource.username=.+/spring.datasource.username=ctu/g' application.properties")  # noqa: W605
    conn.run("sed -i -E 's/^spring.datasource.druid.username=.+/spring.datasource.druid.username=ctu/g' application.properties")
    conn.run("sed -i -E 's/[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+/%s/g' application.properties" % _DB_HOST)  # noqa: W605
    conn.run("sed -i -E 's/jdbc:mysql:\/\/[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+:[0-9]+\/[a-z0-9_-]+\?/jdbc:mysql:\/\/mysql-1.dx.corp:3306\/%s?/g' application.properties" % db_name)  # noqa: W605
    conn.run("sed -i -E 's/[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+:7776/%s:7776/g' application.properties" % conn.host)  # noqa: W605
    conn.run("sed -i -E 's/[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+:7090/%s:7090/g' application.properties" % conn.host)  # noqa: W605
    conn.run("sed -i -E 's/^es.clusterNodes=.+/es.clusterNodes=es-1.dx.corp:9300,es-2.dx.corp:9300/g' application.properties")
    conn.run("sed -i -E 's/^ipRegionFile=.+/ipRegionFile=\/home\/admin\/ip2region.db/g' application.properties")  # noqa: W605
    conn.run("sed -i -E 's/^phoneGeoFile=.+/phoneGeoFile=\/home\/admin\/phone.dat/g' application.properties")  # noqa: W605
    conn.run("sed -i -E 's/^mobile\.kvFile\.ios=.+/mobile.kvFile.ios=\/home\/admin\/ios_key_map.txt/g' application.properties")  # noqa: W605
    conn.run("sed -i -E 's/^mobile\.kvFile\.android=.+/mobile.kvFile.android=\/home\/admin\/android_key_map.txt/g' application.properties")  # noqa: W605
    conn.run("sed -i -E 's/^constid\.http\.filed=.+/constid.http.filed=\/home\/admin\/constid_filed_map.txt/g' application.properties")  # noqa: W605
    conn.run("sed -i -E 's/^manager.review=.+/manager.review=true/g' application.properties")
    conn.run("sed -i -E 's/^captcha.images.background.app.+/captcha.images.background.app=\/home\/admin\/captcha\/image\/app/g' application.properties")  # noqa: W605
    conn.run("sed -i -E 's/^captcha.images.background.default.+/captcha.images.background.default=\/home\/admin\/captcha\/image\/default/g' application.properties")  # noqa: W605
    conn.run("sed -i -E 's/^captcha.images.water.file.+/captcha.images.water.file=\/home\/admin\/captcha\/image\/water/g' application.properties")  # noqa: W605
    conn.run("sed -i -E 's/^spring.dubbo.registry.address=.+/spring.dubbo.registry.address=zookeeper:\/\/%s:2181/g' application.properties" % conn.host)  # noqa: W605
    conn.run("sed -i -E 's/^dubbo.registry.zookeeper.address=.+/dubbo.registry.zookeeper.address=%s:2181/g' application.properties" % conn.host)
    conn.run("sed -i -E 's/^cookie.check=.+/cookie.check=true/g' application.properties")
    conn.run("sed -i -E 's/^mongo.isCluster=.+/mongo.isCluster=false/g' application.properties")
    conn.run("sed -i -E 's/^mongo.auth=.+/mongo.auth=false/g' application.properties")
    conn.run("sed -i -E 's/^mongo.hosts=.+/mongo.hosts=mongo-1.dx.corp:27017/g' application.properties")
    conn.run("sed -i -E 's/^datasource.host=.+/datasource.host=mysql-1.dx.corp/g' application.properties")
    conn.run("sed -i -E 's/^datasource.port=.+/datasource.port=3306/g' application.properties")
    conn.run("sed -i -E 's/^datasource.name=.+/datasource.name=%s/g' application.properties" % db_name)
    conn.run("sed -i -E 's/^spring.datasource.url=.+/spring.datasource.url=jdbc:mysql:\/\/mysql-1.dx.corp:3306\/%s\?useUnicode=true\&characterEncoding=utf8\&autoReconnect=true\&allowMultiQueries=true\&useSSL=false\&serverTimezone=Asia\/Shanghai\&useJDBCCompliantTimezoneShift=true\&useLegacyDatetimeCode=false/g' application.properties" % db_name)


_APP_CONF_UPDATE_MAP = {
    'ctu-console-ui': _update_nginx_conf_and_config_json,
    'credit-console': _update_nginx_conf_and_config_json,
    'default': _update_application_properties}


def _update_conf(conn, app, img_path):
    # under docker directory
    if not conn.reset_conf:
        try:
            conn.run('test -e %s/%s' % (app.name, app.name == 'ctu-console-ui' and 'nginx.conf' or 'application.properties'))
            _echo('skip conf update step')
            return
        except UnexpectedExit:
            _echo('conf file does not exist!')
    container_id = conn.run('docker create ' + img_path).stdout.strip()
    with conn.cd(app.name):
        try:
            func = _APP_CONF_UPDATE_MAP.get(app.name, _APP_CONF_UPDATE_MAP['default'])
            func(conn, container_id)
        finally:
            conn.run('docker rm ' + container_id)


def _start_app(conn, app, img_path):
    # under docker directory
    if app.name == 'ctu-console-ui':
        mount = '-v $PWD/%(name)s/config.json:/usr/local/nginx/html/config.json -v $PWD/%(name)s/config.json:/usr/share/nginx/html/config.json -v $PWD/%(name)s/nginx.conf:/usr/local/nginx/conf/nginx.conf -v $PWD/%(name)s/nginx.conf:/etc/nginx/nginx.conf -v $PWD/%(name)s/logs:/usr/local/nginx/logs' % {'name': app.name}
    elif app.name == 'monitor-agent':
        mount = '-v /:/rootfs:ro -v /sys:/sys:ro -v $PWD/%(name)s/application.properties:/home/admin/application.properties -v $PWD/%(name)s/logs:/home/admin/logs' % {'name': app.name}
    else:
        mount = '-v $PWD/%(name)s/application.properties:/home/admin/application.properties -v $PWD/%(name)s/logs:/home/admin/logs' % {'name': app.name}
    if app.name in _JMX_PORT_MAP:
        jmx_param = _JMX_PARAM % {'host': conn.host, 'port': _JMX_PORT_MAP[app.name]}
    else:
        jmx_param = ''
    cmd = 'docker run --restart on-failure:10 -d --network host -m 3g --log-opt max-size=256m --name %(name)s %(mount)s %(img)s %(jmx)s' % {
        'name': app.name,
        'mount': mount,
        'img': img_path,
        'jmx': jmx_param}
    _echo(cmd)
    conn.run(cmd)


def _echo(msg, **kwargs):
    click.echo('%s %s' % (maya.now().iso8601(), msg), **kwargs)
