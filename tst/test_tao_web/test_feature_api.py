import ujson
from bson import ObjectId
from tao.web.api.common import get_feature_detail
from test_common import MockRequest
from tao.models import Feature, Component, Product
from tao.utils import AIterList, read_async_result


def test_get_feature_detail_without_record(monkeypatch):
    request = MockRequest()
    feature_id = 'a' * 24

    async def mock_find_feature(filter_):
        return None

    monkeypatch.setattr(Feature, 'find_one', mock_find_feature)
    resp = read_async_result(get_feature_detail(request, feature_id))
    assert resp.status == 200
    assert ujson.loads(resp.body) == {}


def test_get_feature_detail_with_record(monkeypatch):
    request = MockRequest()
    feature_id = 'a' * 24

    async def mock_find_product(filter_, fields):
        return {'name': '私有化风控'}

    async def mock_find_feature(filter_):
        return {
                'branch': "feature_20181010_ci_style_check",
                'cci': [
                    {
                        "sha": "d6763b370076a49e208afac10ece923b20830720",
                        "status": "failed",
                        "web_url": "https:\/\/dev.dingxiang-inc.com:2020\/ctu-group\/ctu-console\/pipelines\/12997",
                        "jobs": [{
                            "id": 54343,
                            "status": "success",
                            "stage": "depend",
                            "name": "deps",
                            "ref": "feature_20181010_ci_style_check",
                            "tag": False,
                            "pipeline": {
                                "id": 12997,
                                "sha": "d6763b370076a49e208afac10ece923b20830720",
                                "ref": "feature_20181010_ci_style_check",
                                "status": "failed",
                                "web_url": "https:\/\/dev.dingxiang-inc.com:2020\/ctu-group\/ctu-console\/pipelines\/12997"}
                            }]
                        }],
                'components': [ObjectId('b'*24), ObjectId('c'*24)],
                'create_time': 1539237190220,
                'dependencies': [],
                'name': "Java代码风格检查",
                'product': ObjectId("5b8fd4630b90c63cefeed312"),
                'status': "new",
                'update_time': 1539237190220,
                '_id': ObjectId(feature_id)}

    def mock_find_components(filter_, fields):
        return AIterList([
            {
                'docker_repo': "harbor.dx-corp.top/ctu-group/ctu-console",
                'name': "ctu-console",
                '_id': ObjectId('b'*24)},
            {
                'docker_repo': "harbor.dx-corp.top/ctu-group/ctu-indictator",
                'name': "ctu-indicator",
                '_id': ObjectId('c'*24)}])

    monkeypatch.setattr(Product, 'find_one', mock_find_product)
    monkeypatch.setattr(Feature, 'find_one', mock_find_feature)
    monkeypatch.setattr(Component, 'find', mock_find_components)
    resp = read_async_result(get_feature_detail(request, feature_id))
    assert resp.status == 200
    body_json = ujson.loads(resp.body)
    assert body_json['status'] == 'new'
    assert body_json['name'] == 'Java代码风格检查'
    assert body_json['components'][0]['name'] == 'ctu-console'
    assert body_json['product_name'] == '私有化风控'
