import pytest
from sanic.exceptions import Unauthorized
from tao.web.__main__ import is_authorized_request
from tao.web import __main__ as main
from test_common import MockRequest
from tao.utils import read_async_result


def test_is_authorized_request(monkeypatch):
    request = MockRequest()
    # whitelist api
    request.session = {}
    request.path = '/api/v1/auth'
    request.ip = '12.34.56.78'
    assert read_async_result(is_authorized_request(request)) is None
    # localhost request for debug
    request.session = {}
    request.path = '/api/v1/products'
    request.ip = '127.0.0.1'
    assert read_async_result(is_authorized_request(request)) is None
    # with user session
    request.session['user'] = {'user': 'mock', 'username': 'mockname'}
    request.path = '/api/v1/products'
    request.ip = '12.34.56.78'
    assert read_async_result(is_authorized_request(request)) is None
    # /api request with unauthorized
    request.session = {}
    request.path = '/api/v1/products'
    request.ip = '12.34.56.78'
    with pytest.raises(Unauthorized):
        read_async_result(is_authorized_request(request))
    # /<!not api> request will redirect to '/api/v1/auth'
    request.session = {}
    request.path = '/index.html'
    request.ip = '12.34.56.78'
    monkeypatch.setattr(main, 'redirect', lambda e: e)
    assert read_async_result(is_authorized_request(request)) == '/api/v1/auth'
