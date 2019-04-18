import maya
from tao.utils import read_async_result, AIterList
from tao.clerk import cron
from tao.clerk.cron import inform_long_time_failed_cci, PipelineStatus, _inform_one_project_branch_failed_cci


def test_inform_long_time_failed_cci(monkeypatch):
    def _mock_pipelinestatus_find(filter_):
        return AIterList([
            {
                'commit_id': 'dee4b2f1d6048bb128422aed4b1458bfe80d619d',
                'project_branch': 'ctu-pci/v2.4.0',
                'create_time': 1548658599,
                'fished_time': 1548658603,
                'send_msg_time': 1548658603,
                'author': 'zhangyu',
                'name': '张裕',
                'status': 'failed',
                'send_msg_times': 1,
            },
            {
                'commit_id': 'dee4b2f1d6048bb128422aed4b1458bfe80d619d',
                'project_branch': 'tao/master',
                'create_time': 1548658099,
                'fished_time': 1548658603,
                'send_msg_time': 1548658603,
                'author': 'test',
                'name': '机器人',
                'status': 'failed',
                'send_msg_times': 1,
            },
            {
                'commit_id': 'dee4b2f1d6048bb128422aed4b1458bfe80d619d',
                'project_branch': 'ctu-pci/v2.4.0',
                'create_time': 1548668599,
                'fished_time': 1548668603,
                'send_msg_time': 1548758603,
                'author': 'www',
                'name': '万维网',
                'status': 'failed',
                'send_msg_times': 1,
            },
        ])

    records = []

    def _mock_inform_one(project_branch, ccis):
        records.append((project_branch, ccis))

    monkeypatch.setattr(PipelineStatus, 'find', _mock_pipelinestatus_find)
    monkeypatch.setattr(cron, '_inform_one_project_branch_failed_cci', _mock_inform_one)
    read_async_result(inform_long_time_failed_cci())
    assert len(records) == 2
    assert len(records[0][1]) == 2
    assert records[0][0] == 'ctu-pci/v2.4.0'
    assert len(records[1][1]) == 1
    assert records[1][0] == 'tao/master'


def test_will_not_inform_one_less_than_4_hours():
    project_branch = 'demo_project/test_branch'
    _1hour_ago = maya.now().subtract(hours=1).epoch
    ccis = [{
        'commit_id': 'dee4b2f1d6048bb128422aed4b1458bfe80d619d',
        'project_branch': 'tao/master',
        'create_time': _1hour_ago,
        'fished_time': _1hour_ago,
        'send_msg_time': _1hour_ago,
        'author': 'test',
        'name': '机器人',
        'status': 'failed',
        'send_msg_times': 1}]
    read_async_result(_inform_one_project_branch_failed_cci(project_branch, ccis))


def test_will_not_inform_one_cnt_over_1_and_over_4_hours_less_than_24hours():
    project_branch = 'demo_project/test_branch'
    _23hour_ago = maya.now().subtract(hours=23).epoch
    ccis = [{
        'commit_id': 'dee4b2f1d6048bb128422aed4b1458bfe80d619d',
        'project_branch': 'tao/master',
        'create_time': _23hour_ago,
        'fished_time': _23hour_ago,
        'send_msg_time': _23hour_ago,
        'author': 'test',
        'name': '机器人',
        'status': 'failed',
        'send_msg_times': 2}]
    read_async_result(_inform_one_project_branch_failed_cci(project_branch, ccis))


def test_only_inform_user_if_cnt_1_and_over_4hours_less_than_24hours(monkeypatch):
    records = []

    async def _mock_PipelineStatus_update_many(filter_, fields):
        records.append(('PipelineStatus', 'update_many', filter_, fields))

    async def _mock_send_msg_to_cci_authors(ccis):
        records.append(('send_cci_authors', ccis))

    monkeypatch.setattr(PipelineStatus, 'update_many', _mock_PipelineStatus_update_many)
    monkeypatch.setattr(cron, '_send_msg_to_cci_authors', _mock_send_msg_to_cci_authors)

    project_branch = 'demo_project/test_branch'
    _23hour_ago = maya.now().subtract(hours=23).epoch
    ccis = [{
        '_id': 'a' * 48,
        'commit_id': 'dee4b2f1d6048bb128422aed4b1458bfe80d619d',
        'project_branch': 'tao/master',
        'create_time': _23hour_ago,
        'fished_time': _23hour_ago,
        'send_msg_time': _23hour_ago,
        'author': 'test',
        'name': '机器人',
        'status': 'failed',
        'send_msg_times': 1}]
    read_async_result(_inform_one_project_branch_failed_cci(project_branch, ccis))
    assert len(records) == 2
    assert records[0][0] == 'send_cci_authors'
    assert records[1][0] == 'PipelineStatus'
    assert records[1][1] == 'update_many'


def test_will_not_inform_if_sent_date_is_the_same_date():
    project_branch = 'demo_project/test_branch'
    _25hour_ago = maya.now().subtract(hours=25).epoch
    ccis = [{
        '_id': 'a' * 48,
        'commit_id': 'dee4b2f1d6048bb128422aed4b1458bfe80d619d',
        'project_branch': 'tao/master',
        'create_time': _25hour_ago,
        'fished_time': _25hour_ago,
        'send_msg_time': maya.now().epoch,
        'author': 'test',
        'name': '机器人',
        'status': 'failed',
        'send_msg_times': 2}]
    read_async_result(_inform_one_project_branch_failed_cci(project_branch, ccis))
    read_async_result(_inform_one_project_branch_failed_cci(project_branch, ccis))


def test_inform_both_user_and_group_if_over_24hours(monkeypatch):
    records = []

    async def _mock_PipelineStatus_update_many(filter_, fields):
        records.append(('PipelineStatus', 'update_many', filter_, fields))

    async def _mock_send_msg_to_cci_authors(ccis):
        records.append(('send_cci_authors', ccis))

    async def _mock_send_msg_to_author_groups(ccis):
        records.append(('send_author_groups', ccis))

    monkeypatch.setattr(PipelineStatus, 'update_many', _mock_PipelineStatus_update_many)
    monkeypatch.setattr(cron, '_send_msg_to_cci_authors', _mock_send_msg_to_cci_authors)
    monkeypatch.setattr(cron, '_send_msg_to_author_groups', _mock_send_msg_to_author_groups)

    project_branch = 'demo_project/test_branch'
    _20hour_ago = maya.now().subtract(hours=20).epoch
    _25hour_ago = maya.now().subtract(hours=25).epoch
    ccis = [{
        '_id': 'a' * 48,
        'commit_id': 'dee4b2f1d6048bb128422aed4b1458bfe80d619d',
        'project_branch': 'tao/master',
        'create_time': _25hour_ago,
        'fished_time': _25hour_ago,
        'send_msg_time': _20hour_ago,
        'author': 'test',
        'name': '机器人',
        'status': 'failed',
        'send_msg_times': 2}]
    read_async_result(_inform_one_project_branch_failed_cci(project_branch, ccis))
    assert len(records) == 3
    assert records[0][0] == 'send_cci_authors'
    assert records[1][0] == 'send_author_groups'
    assert records[2][0] == 'PipelineStatus'
    assert records[2][1] == 'update_many'
