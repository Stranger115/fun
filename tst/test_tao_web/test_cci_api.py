from asyncio.locks import Lock
from sanic.exceptions import SanicException
from tao.web.api import cci
from tao.web.api.cci import cci_bp, acquire_cci_lock, release_cci_lock
from test_common import MockRequest
from tao.utils import read_async_result


def setup():
    cci_bp.lock = Lock()
    cci_bp.cache = {}


def test_cci_lock(monkeypatch):
    def _get_lock(namespace, project, branch, owner):
        request = MockRequest(
            namespace=namespace,
            project=project,
            branch=branch,
            owner=owner)
        try:
            resp = read_async_result(acquire_cci_lock(request))
            return resp.status
        except SanicException as err:
            return err.status_code

    monkeypatch.setattr(cci, '_LOCK_DURATION', 0.1)
    assert _get_lock('ctu', 'test', 'test', 12345) == 200
    assert _get_lock('ctu', 'test', 'test', 12345) == 200
    assert _get_lock('ctu2', 'test', 'test', 22) == 200

    read_async_result(release_cci_lock(MockRequest(
        namespace='ctu2', project='test', branch='test', owner=22)))

    assert _get_lock('ctu2', 'test', 'test', 33) == 200
