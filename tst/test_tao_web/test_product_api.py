import ujson
from bson import ObjectId
from tao.web.api.common import get_products
from tao.models import Product, Component, Release, Feature, Environment, Pipeline
from test_common import MockRequest
from tao.utils import read_async_result, AIterList


def test_get_products(monkeypatch):
    def mock_find_product(filter_):
        return AIterList([{
            '_id': ObjectId('0' * 24),
            'components': [ObjectId('a'*24), ObjectId('b'*24)],
            'name': 'test product',
            'export_script': 'echo "aaa"'}])

    def mock_find_components(filter_):
        return AIterList([
            {'_id': ObjectId('a'*24), 'name': 'component-a'},
            {'_id': ObjectId('b'*24), 'name': 'component-b'}])

    async def mock_find_release(filter_, **kwargs):
        return None

    def mock_count_documents(count):
        async def _mock(filter_):
            return count
        return _mock

    monkeypatch.setattr(Product, 'find', mock_find_product)
    monkeypatch.setattr(Component, 'find', mock_find_components)
    monkeypatch.setattr(Release, 'find_one', mock_find_release)
    monkeypatch.setattr(Release, 'count_documents', mock_count_documents(0))
    monkeypatch.setattr(Feature, 'count_documents', mock_count_documents(2))
    monkeypatch.setattr(Environment, 'count_documents', mock_count_documents(1))
    resp = read_async_result(get_products(MockRequest()))
    assert resp.status == 200
    body = ujson.loads(resp.body)
    assert body[0]['name'] == 'test product'
    assert body[0]['export_script'] == 'echo "aaa"'
    assert body[0]['components'][0]['name'] == 'component-a'
    assert body[0]['features']['total'] == 2

