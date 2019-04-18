from tao.web.api.common import get_version
from test_common import MockRequest
from tao.utils import read_async_result


def test_get_version():
    resp = read_async_result(get_version(MockRequest()))
    assert resp.status == 200
    assert resp.body == b'{"version":"master"}'
