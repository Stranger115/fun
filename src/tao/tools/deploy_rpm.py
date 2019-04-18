import maya
import click
from collections import namedtuple
from fabric import Connection, Config


def _validate_app(ctx, param, value):
    apps = []
    AppDeploy = namedtuple('AppDeploy', ('name', 'version'))
    for app in value:
        if ':' not in app or app[0] == ':' or app[-1] == ':':
            raise click.BadParameter('app should be format like <name>:<version>')
        name, version = app.split(':', 1)
        apps.append(AppDeploy(name, version))
    return apps


@click.command('deploy_rpm', context_settings={
    'ignore_unknown_options': True,
    'allow_extra_args': True})
@click.option('--host', '-h', required=True, help='host to deploy')
@click.option('--user', '-u', default='root', help='user name of SSH login, default is root')
@click.option('--password', '-p', default='dingxiang-inc@2018', help='password of SSH login')
@click.option('--component', '-c', multiple=True, required=True, callback=_validate_app, help='component to deploy, format: <name>:<version>')
def deploy(host, user, password, component):
    ''' deploy services to specified machine via fabric
        example:
        python3 -m tao.tools deploy_rpm -h 10.1.2.13 -p dx@666 -c falcon-api:1.0 -c falcon-graph:1.1
    '''
    config = Config(overrides={'sudo': {'password': password}})
    if not component:
        _echo("no components to deploy")
        raise RuntimeError
    with Connection(host, user, config=config, connect_kwargs={'password': password}) as conn:
        conn.run('yum clean all')
        for app_item in component:
            _do_deploy(conn, app_item)
        _echo('done')


def _do_deploy(conn, app):
    _echo('start to deploy %s:%s' % (app.name, app.version))
    conn.run('yum install -y %s-%s' % (app.name, app.version))


def _echo(msg, **kwargs):
    click.echo('%s %s' % (maya.now().iso8601(), msg), **kwargs)
