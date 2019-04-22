import os
import logging
import aiohttp
import ujson
import tracemalloc
from sanic import Sanic
from sanic_auth import Auth
from sanic.response import redirect, json
from sanic.exceptions import Unauthorized
from sanic_session import Session, InMemorySessionInterface
from tao.models import init_db
from tao.settings import API_WHITELIST
from .api import product_bp, user_bp, role_bp


_www_build_path = os.path.join(os.path.dirname(__file__), 'www', 'build')


def _join(path):
    return os.path.join(_www_build_path, path)


app = Sanic()
session = Session(app, interface=InMemorySessionInterface())

app.config.AUTH_LOGIN_ENDPOINT = 'login'
auth = Auth(app)


app.blueprint(product_bp)
app.blueprint(user_bp)
app.blueprint(role_bp)

app.static('/static', _join('static'))
app.static('/index.html', _join('index.html'))
app.static('/favicon.ico', _join('favicon.ico'))
app.static('/taflibrary.html', _join('taflibrary.html'))
app.static('/tafFuncLib.html', _join('tafFuncLib.html'))
app.static('/manifest.json', _join('manifest.json'))


@app.listener('before_server_start')
async def init(app, loop) -> None:
    init_db(loop)
    app.async_session = aiohttp.ClientSession(loop=loop, json_serialize=ujson.dumps)
    _snapshots.append(None)
    _snapshots.append(_get_snapshot())


@app.listener('before_server_stop')
async def teardown(app, loop) -> None:
    await app.async_session.close()

@app.middleware('request')
async def is_authorized_request(request):
    # if request.path in API_WHITELIST:  # whitelist
    #     return

    # if request.ip == '127.0.0.1':  # localhost
    #     return
    #
    # if 'user' not in request['session']:
    #     if not request.path.startswith('/api'):  # resource file
    #         logging.debug('auth check failed, redirect to auth url')
    #         return redirect('/api/v1/auth')
    #     raise Unauthorized('unauthorized')
    request['session'] = session
    return

auth = Auth(app)


@app.get('/')
async def index(request):
    return redirect('/index.html')


_snapshots = []  # [old, new] for compare


def _get_snapshot():
    snapshot = tracemalloc.take_snapshot()
    return snapshot.filter_traces((
        tracemalloc.Filter(False, '<frozen importlib._bootstrap>'),
        tracemalloc.Filter(False, '<frozen importlib._bootstrap_external>'),
        tracemalloc.Filter(False, '<unknown>'),
        tracemalloc.Filter(False, tracemalloc.__file__)))


@app.get('/api/v1/debug/memory')
async def show_server_status(request):
    cnt = int(request.args.get('limit', 10))
    _snapshots[0], _snapshots[1] = _snapshots[1], _get_snapshot()
    top_stats = _snapshots[1].compare_to(_snapshots[0], 'lineno')[:cnt]
    return json(top_stats)


def _clear_logging():
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)


if __name__ == '__main__':
    tracemalloc.start()
    _clear_logging()
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s %(levelname)6s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')
    app.run(host='0.0.0.0', port=19898)
