from tao.web.hooks import WebHookHandlers
from tao.utils import read_async_result


def test_on_event(monkeypatch):
    assert 'Pipeline Hook' in WebHookHandlers._handlers
    assert 'Merge Request Hook' in WebHookHandlers._handlers
    assert 'Push Hook' in WebHookHandlers._handlers

    result = {}

    async def _mock_handle_pipeline(event):
        result['pipeline'] = True

    monkeypatch.setattr(WebHookHandlers, '_handlers', {'Pipeline Hook': {_mock_handle_pipeline}})
    read_async_result(WebHookHandlers.on_event('Pipeline Hook', {}))
    assert result.get('pipeline') is True
