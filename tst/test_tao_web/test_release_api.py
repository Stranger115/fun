import ujson
from bson import ObjectId
from tao.web.api.common import get_release_detail
from test_common import MockRequest
from tao.utils import AIterList, read_async_result
from tao.models import Release, Component, Product, Feature, MergeRequest


def test_get_release_detail_without_record(monkeypatch):
    request = MockRequest()
    release_id = 'a' * 24

    async def mock_find_release(filter_):
        return None

    monkeypatch.setattr(Release, 'find_one', mock_find_release)
    resp = read_async_result(get_release_detail(request, release_id))
    assert resp.status == 200
    assert ujson.loads(resp.body) == {}


def test_get_release_detail_with_record(monkeypatch):
    request = MockRequest()
    release_id = 'a' * 24

    async def mock_find_release(filter_):
        return {
                '_id': ObjectId(release_id),
                'name': 'v2.3.0',
                'branch': 'release_20181015_monthly',
                'product': ObjectId('1' * 24),
                'base_version': 'v2.2.2',
                'features': [ObjectId('b' * 24), ObjectId('c' * 24)],
                'status': 'new',
                'create_time': 1539571248223,
                'update_time': 1539571248223,
                'cci': [],
                'pci': []}

    async def mock_find_product(filter_, fileds):
        return {
                '_id': ObjectId('1' * 24),
                'name': '私有化风控',
                'components': [
                    ObjectId('0' * 24),
                    ObjectId('b' * 24),
                    ObjectId('c' * 24),
                    ObjectId('d' * 24),
                    ObjectId('e' * 24),
                    ]}

    def mock_find_features(filter_, fields):
        return AIterList([
                {
                    '_id': ObjectId('b' * 24),
                    'name': 'unit test',
                    'status': 'new',
                    'components': [ObjectId('0' * 24)],
                    'create_time': 13458900324},
                {
                    '_id': ObjectId('c' * 24),
                    'name': 'acceptance test',
                    'status': 'new',
                    'components': [ObjectId('b' * 24)],
                    'create_time': 13458904024}])

    def mock_find_components(filter_, fields):
        return AIterList([
                {
                    '_id': ObjectId('0' * 24),
                    'name': '0 test',
                    'status': 'new',
                    'tags': ['v1.0', 'v2.0'],
                    'create_time': 13458900324},
                {
                    '_id': ObjectId('b' * 24),
                    'name': 'unit test',
                    'status': 'new',
                    'tags': ['v1.0', 'v2.0'],
                    'create_time': 13458900324},
                {
                    '_id': ObjectId('c' * 24),
                    'name': 'acceptance test',
                    'status': 'new',
                    'create_time': 13458904024},
                {
                    '_id': ObjectId('d' * 24),
                    'name': 'd test',
                    'status': 'new',
                    'create_time': 13458904024},
                {
                    '_id': ObjectId('e' * 24),
                    'name': 'e test',
                    'status': 'new',
                    'create_time': 13458904024},
                ])

    def mock_find_merge_requests(filter_):
        return AIterList([{
            'can_be_merged': False,
            'component': ObjectId('b' * 24),
            'downvotes': 0,
            'project_id': 32,
            'source_branch': 'feature_20181010_hotfix_from_master',
            'state': 'closed',
            'target_branch': 'master',
            'upvotes': 0,
            'web_url': 'https://dev.dingxiang-inc.com:2020/ctu-group/ctu-console/merge_requests/63',
            '_id': '5bbdf02697229a57502e0016',
            }])

    monkeypatch.setattr(Release, 'find_one', mock_find_release)
    monkeypatch.setattr(Product, 'find_one', mock_find_product)
    monkeypatch.setattr(Feature, 'find', mock_find_features)
    monkeypatch.setattr(Component, 'find', mock_find_components)
    monkeypatch.setattr(MergeRequest, 'find', mock_find_merge_requests)
    resp = read_async_result(get_release_detail(request, release_id))
    assert resp.status == 200
    data = ujson.loads(resp.body)
    assert data['name'] == 'v2.3.0'
    assert data['branch'] == 'release_20181015_monthly'
    assert data['features'][0]['name'] == 'unit test'
    assert data['features'][0]['components'][0]['name'] == '0 test'
    assert data['features'][0]['components'][0]['tags'][0] == 'v1.0'
    assert data['merge_requests'][0]['project_id'] == 32
