import pytest
from tao.common.dingding import DingdingProxy, FetchAccessTokenFailed
from tao.utils import read_async_result
from tao.settings import DINGDING_AGENT_API


def test_dingding_request_fetch_access_token_failed(monkeypatch):
    monkeypatch.setattr(DingdingProxy, 'session', _MockSession([{
        'errmsg': 'err',
        'errcode': 1002}]))
    with pytest.raises(FetchAccessTokenFailed):
        read_async_result(DingdingProxy._post(DINGDING_AGENT_API, {}))


def test_dingding_request_access_token_expired(monkeypatch):
    monkeypatch.setattr(DingdingProxy, 'access_token', '8a6ca6e686363a8db891a5c9f10a650a')
    monkeypatch.setattr(DingdingProxy, 'session', _MockSession([
        {'errmsg': '不合法的access_token', 'errcode': 40014},
        {'errmsg': 'ok', 'errcode': 0, 'access_token': '8a6ca6e686363a8db891a5c9f10a650b'},
        {'errmsg': 'ok', 'errcode': 0},
    ]))
    read_async_result(DingdingProxy._post(DINGDING_AGENT_API, {}))


def test_dingding_request_without_access_token(monkeypatch):
    monkeypatch.setattr(DingdingProxy, 'session', _MockSession([
        {'errmsg': 'ok', 'errcode': 0, 'access_token': '8a6ca6e686363a8db891a5c9f10a650b'},
        {'errmsg': 'ok', 'errcode': 0},
    ]))
    read_async_result(DingdingProxy._post(DINGDING_AGENT_API, {}))


class _MockSession(object):
    def __init__(self, mock_result):
        self._mock_result = iter(mock_result)

    def get(self, *args, **kwargs):
        return _MockResponse(next(self._mock_result))

    def post(self, *args, **kwargs):
        return _MockResponse(next(self._mock_result))


class _MockResponse(object):
    def __init__(self, data):
        self.data = data

    async def __aenter__(self):
        return self

    async def json(self):
        return self.data

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
