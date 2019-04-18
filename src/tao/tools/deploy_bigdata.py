import maya
import click
from collections import namedtuple
from fabric import Connection, Config

_FTP_HOST = "10.1.2.14"
_FTP_USER = "ctuftp"
_FTP_PASSWD = "ctuftp"


def _validate_app(ctx, param, value):
    apps = []
    AppDeploy = namedtuple('AppDeploy', ('name', 'version'))
    for app in value:
        if ':' not in app or app[0] == ':' or app[-1] == ':':
            raise click.BadParameter('app should be format like <name>:<version>')
        name, version = app.split(':', 1)
        apps.append(AppDeploy(name, version))
    return apps


@click.command('deploy_bigdata', context_settings={
    'ignore_unknown_options': True,
    'allow_extra_args': True})
@click.option('--host', '-h', required=True, help='host to deploy')
@click.option('--user', '-u', default='root', help='user name of SSH login, default is root')
@click.option('--password', '-p', default='dingxiang-inc@2018', help='password of SSH login')
@click.option('--version', '-v', default='', help='version to deploy')
@click.option('--resetdb', '-r', is_flag=True, help='if set, will reset database')
@click.option('--resetconf', '-f', is_flag=True, help='if set, will reset configuration')
@click.option('--component', '-c', multiple=True, required=True, callback=_validate_app, help='component to deploy, format: <name>:<version>')
def deploy(host, user, password, version, resetdb, resetconf, component):
    ''' deploy services to specified machine via fabric
        example:
        python3 -m tao.tools deploy_bigdata -h 10.1.2.13 -p dx@666 -c usercenter:master -c console:master
        python  -m tao.tools deploy_bigdata -h 10.1.2.138 -u dingxiang -p dx@666 -c usercenter:feature/feature_20181211_ci
    '''
    config = Config(overrides={'sudo': {'password': password}})
    if not component:
        _echo("no components to deploy")
        raise RuntimeError
    with Connection(host, user, config=config, connect_kwargs={'password': password}) as conn:
        conn.version = version
        conn.reset_db = resetdb
        conn.reset_conf = resetconf
        for app_item in component:
            _echo('start to deploy %s:%s' % (app_item.name, app_item.version))
            _do_deploy(conn, app_item)
        _echo('done')


def _do_deploy(conn, app):
    _echo('start to deploy %s:%s' % (app.name, app.version))
    if app.name == "usercenter" or app.name == "webconsole" or app.name == "aip" or app.name == "datax" or app.name == "azkaban" or app.name == "flume":
        if app.name == "webconsole":
            profile = "cloudera"
        else:
            profile = ""
        _do_dw_deploy(conn,app,profile)
    if app.name == "ui":
        _do_ui_deploy(conn,app)
    if app.name == "cm-csd":
        _do_csd_deploy(conn,app)

def _do_dw_deploy(conn,app,profile):
        app_name = app.name
        conn.run("sh /opt/cloudera/parcels/.cleanOldParcel.sh %s %s" % (app_name.upper(), app.version))
        if app.version != "pre":
            conn.run("curl -O -u %s:%s ftp://%s/qianxiang/%s/%s/%s-%s-el7.parcel" % (_FTP_USER,_FTP_PASSWD,_FTP_HOST,app.version,profile, app_name.upper(), app.version))
            conn.run("curl -O -u %s:%s ftp://%s/qianxiang/%s/%s/%s-%s-el7.parcel.sha" % (_FTP_USER,_FTP_PASSWD,_FTP_HOST,app.version,profile, app_name.upper(), app.version))
            conn.run("mv %s-%s-el7.parcel* /opt/cloudera/parcel-repo" % (app_name.upper(), app.version))
        conn.run("sh /opt/cloudera/parcels/.deployNewParcel.sh %s %s" % (app_name.upper(), app.version))


def _do_csd_deploy(conn, app):

        if app.version != "pre":
            conn.run("curl -O -u %s:%s ftp://%s/qianxiang/%s/csd.tar.gz" % (_FTP_USER,_FTP_PASSWD,_FTP_HOST,app.version))
            conn.run("tar -zxvf csd.tar.gz -C /opt/cloudera/csd")
        else :
            conn.run("/opt/cloudera/csd/.deploy.sh")
        conn.run("/opt/cloudera/csd/.reinstall.sh")


def _do_ui_deploy(conn,app):
    _echo('ui deploy')


def _echo(msg, **kwargs):
    click.echo('%s %s' % (maya.now().iso8601(), msg), **kwargs)
