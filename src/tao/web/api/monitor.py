from sanic import Blueprint
from sanic.response import json
from tao.models import Environment


monitor_bp = Blueprint('monitor')


@monitor_bp.get('/api/v1/monitor/hosts')
async def get_hosts(request):
    return json([{
        'name': e['name'],
        'roles': [],
        'maintaining': e['status'] == Environment.MAINTAINED
    } async for e in Environment.find({}, ['name', 'status'])])


@monitor_bp.get('/api/v1/monitor/aggrs')
async def get_aggregators(request):
    # TODO:
    return json([])


@monitor_bp.get('/api/v1/monitor/nodata')
async def get_nodatas(request):
    return json([{
        'name': 'nodata.all.agent.alive',
        'endpoint': e['name'],
        'metric': 'agent.alive',
        'tags': {},
        'type': 'GAUGE',
        'step': 60,
        'mock': 0} async for e in Environment.find({}, ['name'])])


_DEFAULT_PLUGINS = ['sys/ntp', 'process']


@monitor_bp.get('/api/v1/monitor/plugins')
async def get_plugins(request):
    plugins = {}
    async for env in Environment.find({}, ['name', 'label']):
        if isinstance(env['label'], list):
            plugins[env['name']] = _DEFAULT_PLUGINS + env['label']
        else:
            plugins[env['name']] = _DEFAULT_PLUGINS

    return json(plugins)


@monitor_bp.get('/api/v1/monitor/strategies')
async def get_strategies(request):
    # TODO:
    return json([])
