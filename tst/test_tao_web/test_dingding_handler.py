from tao.web.hooks.dingding_handler import send_dingding_message_on_updated_failed_pipeline, PipelineStatus, DingdingProxy, DingDingUser
from tao.utils import read_async_result, AIterList


def test_trigger_dingding_on_success_pipeline(monkeypatch):
    records = []

    async def _mock_PipelineStatus_find_one_exist_new(filter_):
        records.append(('find_one', filter_))
        return {
            '_id': "5c4e700859af07000a125e1a",
            'commit_id': "41d85cef16a80417a4f3ef03140fbc9a122cb1c4",
            'project_branch': "tao/master",
            'create_time': 1530031043,
            'fished_time': 1530031072,
            'send_msg_time': 1530031072,
            'status': "failed",
            'send_msg_times': 1}

    async def _mock_PipelineStatus_find_one_not_exist(filter_):
        records.append(('find_one', filter_))
        return None

    async def _mock_PipelineStatus_upsert(filter_, fields, **kwargs):
        records.append(('upsert', filter_, fields, kwargs))

    async def _mock_PipelineStatus_create(**fields):
        records.append(('create', fields))

    async def _mock_PipelineStatus_delete_many(filter_):
        records.append(('delete_many', filter_))

    monkeypatch.setattr(PipelineStatus, 'upsert', _mock_PipelineStatus_upsert)
    monkeypatch.setattr(PipelineStatus, 'create', _mock_PipelineStatus_create)
    monkeypatch.setattr(PipelineStatus, 'delete_many', _mock_PipelineStatus_delete_many)

    event = {
        'object_kind': 'pipeline',
        'object_attributes': {
            'id': 10145,
            'ref': 'master',
            'tag': False,
            'sha': '14f7ea23077d1310454a1cad835d8c0ba4028a58',
            'before_sha': '28da57f5a1fef14381a9bc753d52b701f3953aaf',
            'status': 'success',
            'detailed_status': 'passed',
            'stages': ['test', 'www', 'package'],
            'created_at': '2018-09-01 02:45:28 UTC',
            'finished_at': '2018-09-02 02:45:28 UTC'
        },
        'user': {
            'name': '张裕',
            'username': 'zhangyu',
            'avatar_url': None
        },
        'project': {
            'id': 602,
            'name': 'tao',
            'web_url': 'https://dev.dingxiang-inc.com:2020/aladdin/tao',
            'avatar_url': None,
            'namespace': 'aladdin',
            'visibility_level': 10,
            'path_with_namespace': 'aladdin/tao',
            'default_branch': 'master',
            'ci_config_path': None
        },
        'commit': {
            'id': 1111,
            'url': 'https://dev.dingxiang-inc.com:2020/aladdin/tao.git/111',
        }
    }

    # not legacy pipeline
    monkeypatch.setattr(PipelineStatus, 'find_one', _mock_PipelineStatus_find_one_not_exist)
    read_async_result(send_dingding_message_on_updated_failed_pipeline(event))
    assert len(records) == 2
    assert records[0][0] == 'find_one'
    assert records[1][0] == 'delete_many'

    # legacy retry pipeline
    monkeypatch.setattr(PipelineStatus, 'find_one', _mock_PipelineStatus_find_one_exist_new)
    read_async_result(send_dingding_message_on_updated_failed_pipeline(event))
    assert len(records) == 3
    assert records[2][0] == 'find_one'


def test_trigger_dingding_on_pending_pipeline():
    event = {
        'object_kind': 'pipeline',
        'object_attributes': {
            'id': 10145,
            'ref': 'master',
            'tag': False,
            'sha': '14f7ea23077d1310454a1cad835d8c0ba4028a58',
            'before_sha': '28da57f5a1fef14381a9bc753d52b701f3953aaf',
            'status': 'pending',
            'detailed_status': 'running',
            'stages': ['test', 'www', 'package'],
            'created_at': '2018-09-01 02:45:28 UTC',
            'finished_at': '2018-09-02 02:45:28 UTC'
        },
    }
    assert read_async_result(send_dingding_message_on_updated_failed_pipeline(event)) is None


def test_trigger_dingding_on_failed_pipeline(monkeypatch):
    records = []
    dingding_sent = []

    async def _mock_dingding_send(title, text, touser):
        dingding_sent.append((title, text, touser))

    def _mock_dingdinguser_find(filter_):
        return AIterList([
            {
                '_id': '5c81da3b1cf9ac000a56ab8c',
                'name': '张裕',
                'gitlab_name': 'zhangyu',
                'dingding_name': 'zhangyu',
                'userid': '0410375944789941',
                'mobile': '13958178337',
                'partyid': 69382500,
                'party_name': '风控产品部一部',
                'parent_id': 69332499,
                'flag': True}])

    def _mock_dingdinguser_not_found(filter_):
        return AIterList([])

    async def _mock_PipelineStatus_find_one_exist_new(filter_):
        records.append(('find_one', filter_))
        return {
            '_id': "5c4e700859af07000a125e1a",
            'commit_id': "41d85cef16a80417a4f3ef03140fbc9a122cb1c4",
            'project_branch': "tao/master",
            'create_time': 1530031043,
            'fished_time': 1530031072,
            'send_msg_time': 1530031072,
            'status': "failed",
            'send_msg_times': 1}

    async def _mock_PipelineStatus_find_one_not_exist(filter_):
        records.append(('find_one', filter_))
        return None

    async def _mock_PipelineStatus_upsert(filter_, fields, **kwargs):
        records.append(('upsert', filter_, fields, kwargs))

    async def _mock_PipelineStatus_create(**fields):
        records.append(('create', fields))

    async def _mock_PipelineStatus_delete_many(filter_):
        records.append(('delete_many', filter_))

    def _mock_PipelineStatus_find(filter_, fields=[]):
        records.append(('find', filter_))
        return AIterList([{'author': 'zhangyu'}])

    monkeypatch.setattr(DingdingProxy, 'send_markdown_message_to_user', _mock_dingding_send)
    monkeypatch.setattr(DingDingUser, 'find', _mock_dingdinguser_find)
    monkeypatch.setattr(PipelineStatus, 'upsert', _mock_PipelineStatus_upsert)
    monkeypatch.setattr(PipelineStatus, 'create', _mock_PipelineStatus_create)
    monkeypatch.setattr(PipelineStatus, 'delete_many', _mock_PipelineStatus_delete_many)
    monkeypatch.setattr(PipelineStatus, 'find', _mock_PipelineStatus_find)

    event = {
        'object_kind': 'pipeline',
        'object_attributes': {
            'id': 10145,
            'ref': 'master',
            'tag': False,
            'sha': '14f7ea23077d1310454a1cad835d8c0ba4028a58',
            'before_sha': '28da57f5a1fef14381a9bc753d52b701f3953aaf',
            'status': 'failed',
            'detailed_status': 'failed',
            'stages': ['test', 'www', 'package'],
            'created_at': '2018-09-01 02:45:28 UTC',
            'finished_at': '2018-09-02 02:45:28 UTC'
        },
        'user': {
            'name': '张裕',
            'username': 'zhangyu',
            'avatar_url': None
        },
        'project': {
            'id': 602,
            'name': 'tao',
            'web_url': 'https://dev.dingxiang-inc.com:2020/aladdin/tao',
            'avatar_url': None,
            'namespace': 'aladdin',
            'visibility_level': 10,
            'path_with_namespace': 'aladdin/tao',
            'default_branch': 'master',
            'ci_config_path': None
        },
        'commit': {
            'id': '080f67c537e6b518cdb1ebaa0009b4610a578393',
            'url': 'https://dev.dingxiang-inc.com:2020/aladdin/tao.git/111',
        }
    }

    # legacy retry pipeline
    monkeypatch.setattr(PipelineStatus, 'find_one', _mock_PipelineStatus_find_one_exist_new)
    read_async_result(send_dingding_message_on_updated_failed_pipeline(event))
    assert len(records) == 1
    assert records[0][0] == 'find_one'
    assert len(dingding_sent) == 0

    # not legacy pipeline, dingding user exist
    monkeypatch.setattr(PipelineStatus, 'find_one', _mock_PipelineStatus_find_one_not_exist)
    read_async_result(send_dingding_message_on_updated_failed_pipeline(event))
    assert len(records) == 4
    assert records[1][0] == 'find_one'
    assert records[2][0] == 'upsert'
    assert records[3][0] == 'find'
    assert len(dingding_sent) == 1
    assert dingding_sent[0][0] == 'tao/master CCI失败'
    assert dingding_sent[0][1] == '''### Warning tao/master CCI失败
#### [Pipeline](https://dev.dingxiang-inc.com:2020/aladdin/tao/pipelines/10145) | [080f67c5](https://dev.dingxiang-inc.com:2020/aladdin/tao.git/111)
##### 最新触发者：张裕
##### 请以下各位同学相互协调工作，尽快修复CI ！
 - 张裕'''
    assert dingding_sent[0][2] == ['0410375944789941']

    # not legacy pipeline, dingding user missing
    monkeypatch.setattr(DingDingUser, 'find', _mock_dingdinguser_not_found)
    read_async_result(send_dingding_message_on_updated_failed_pipeline(event))
    assert len(records) == 7
    assert records[1][0] == 'find_one'
    assert records[2][0] == 'upsert'
    assert records[3][0] == 'find'
    assert len(dingding_sent) == 2
    assert dingding_sent[1][0] == 'GitLab USER 404 NOT FOUND'
    assert dingding_sent[1][1] == 'GitLab Users: zhangyu'
    assert dingding_sent[1][2] == ['0410375944789941']
