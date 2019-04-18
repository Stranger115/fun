import pytest
import asyncio
from tao.models import Feature, Product, Task, Component, Release
from tao.clerk.runner import TaskRunner, _PublishTaskHandler, TaskFailed
from tao.utils import AIterList, read_async_result
from tao.clerk.gitlab_wrapper import GitlabApiWrapper


@pytest.fixture(autouse=True)
def mock_add_log(monkeypatch):
    async def _mock_task_add_log(*args):
        return
    monkeypatch.setattr(Task, 'add_log', _mock_task_add_log)


@pytest.fixture(autouse=True)
def mock_sleep(monkeypatch):
    async def _mock_sleep(*args):
        return
    monkeypatch.setattr(asyncio, 'sleep', _mock_sleep)


def test_runner_scan():
    assert list(TaskRunner._scan_runners().keys()) == [
        'deploy', 'publish', 'trigger_cci']


# 1. no base_release
# 2. have base_release, components is the same
# 3. have base_release, components is the different, latest release
# 4. have base_release, components is the different, not latest release
def test_get_legacy_and_updated_components_with_no_base_release(monkeypatch):
    task = {'_id': 't1' * 12, 'args': {'release_id': 'a' * 24}}
    components = [
        {'_id': 'c1' * 12, 'gitlab_project_id': 10001, 'name': 'c1'},
        {'_id': 'c2' * 12, 'gitlab_project_id': 10002, 'name': 'c2'},
        {'_id': 'c3' * 12, 'gitlab_project_id': 10003, 'name': 'c3'},
        {'_id': 'c4' * 12, 'gitlab_project_id': 10004, 'name': 'c4'}]

    release = {
        'name': 'v2.3.0',
        'branch': 'release_20181212_utest',
        'product': 'p' * 24,
        'features': ['f1' * 12, 'f2' * 12]}

    async def _mock_product_find_one(filter_):
        return {
            'components': [c['_id'] for c in components]}

    def _mock_feature_find(filter_):
        return AIterList([
            {
                '_id': 'f1' * 12,
                'components': ['c1' * 12, 'c2' * 12]},
            {
                '_id': 'f2' * 12,
                'components': ['c1' * 12, 'c3' * 12, 'c4' * 12]}])

    def _mock_component_find(filter_):
        return AIterList([c for c in components if c['_id'] in filter_['_id']['$in']])

    monkeypatch.setattr(Product, 'find_one', _mock_product_find_one)
    monkeypatch.setattr(Feature, 'find', _mock_feature_find)
    monkeypatch.setattr(Component, 'find', _mock_component_find)

    updated, legacy = read_async_result(_PublishTaskHandler(task)._get_updated_and_legacy_components(release, None, True))
    assert updated == [
        {'_id': 'c1' * 12, 'gitlab_project_id': 10001, 'name': 'c1'},
        {'_id': 'c2' * 12, 'gitlab_project_id': 10002, 'name': 'c2'},
        {'_id': 'c3' * 12, 'gitlab_project_id': 10003, 'name': 'c3'},
        {'_id': 'c4' * 12, 'gitlab_project_id': 10004, 'name': 'c4'}]
    assert legacy == []

    updated, legacy = read_async_result(_PublishTaskHandler(task)._get_updated_and_legacy_components(release, None, False))
    assert updated == [
        {'_id': 'c1' * 12, 'gitlab_project_id': 10001, 'name': 'c1'},
        {'_id': 'c2' * 12, 'gitlab_project_id': 10002, 'name': 'c2'},
        {'_id': 'c3' * 12, 'gitlab_project_id': 10003, 'name': 'c3'},
        {'_id': 'c4' * 12, 'gitlab_project_id': 10004, 'name': 'c4'}]
    assert legacy == []


def test_get_legacy_and_updated_components_with_base_release_and_same_components(monkeypatch):
    task = {'_id': 't1' * 12, 'args': {'release_id': 'a' * 24}}
    components = [
        {'_id': 'c1' * 12, 'gitlab_project_id': 10001, 'name': 'c1'},
        {'_id': 'c2' * 12, 'gitlab_project_id': 10002, 'name': 'c2'},
        {'_id': 'c3' * 12, 'gitlab_project_id': 10003, 'name': 'c3'},
        {'_id': 'c4' * 12, 'gitlab_project_id': 10004, 'name': 'c4'}]

    release = {
        'name': 'v2.3.1',
        'branch': 'release_20181212_utest',
        'base_version': 'v2.3.0',
        'product': 'p' * 24,
        'features': ['f1' * 12, 'f2' * 12]}
    base_release = {
        'name': 'v2.3.0',
        'branch': 'release_20181111_utest',
        'product': 'p' * 24,
        'features': ['f0' * 12],
        'publish': {
            "by": "ci",
            "at": 1543922987726,
            "components": [
                {
                    '_id': 'c1' * 12,
                    'name': 'c1',
                    'type': 'app',
                    'docker_repo': 'docker-c1',
                    'version': 'v2.3.0'
                },
                {
                    '_id': 'c2' * 12,
                    'name': 'c2',
                    'type': 'app',
                    'docker_repo': 'docker-c2',
                    'version': 'v2.3.0'
                },
                {
                    '_id': 'c3' * 12,
                    'name': 'c3',
                    'type': 'app',
                    'docker_repo': 'docker-c3',
                    'version': 'v2.3.0'
                },
                {
                    '_id': 'c4' * 12,
                    'name': 'c4',
                    'type': 'sql',
                    'docker_repo': '',
                    'version': 'v2.3.0'
                },
            ]}}

    async def _mock_product_find_one(filter_):
        return {
            'components': [c['_id'] for c in components]}

    def _mock_feature_find(filter_):
        return AIterList([
            {
                '_id': 'f1' * 12,
                'components': ['c1' * 12]},
            {
                '_id': 'f2' * 12,
                'components': ['c1' * 12, 'c2' * 12]}])

    def _mock_component_find(filter_):
        return AIterList([c for c in components if c['_id'] in filter_['_id']['$in']])

    monkeypatch.setattr(Product, 'find_one', _mock_product_find_one)
    monkeypatch.setattr(Feature, 'find', _mock_feature_find)
    monkeypatch.setattr(Component, 'find', _mock_component_find)

    updated, legacy = read_async_result(_PublishTaskHandler(task)._get_updated_and_legacy_components(release, base_release, True))
    assert updated == [
        {'_id': 'c1' * 12, 'gitlab_project_id': 10001, 'name': 'c1'},
        {'_id': 'c2' * 12, 'gitlab_project_id': 10002, 'name': 'c2'}]
    assert legacy == [
        {'_id': 'c3' * 12, 'gitlab_project_id': 10003, 'name': 'c3'},
        {'_id': 'c4' * 12, 'gitlab_project_id': 10004, 'name': 'c4'}]

    updated, legacy = read_async_result(_PublishTaskHandler(task)._get_updated_and_legacy_components(release, base_release, False))
    assert updated == [
        {'_id': 'c1' * 12, 'gitlab_project_id': 10001, 'name': 'c1'},
        {'_id': 'c2' * 12, 'gitlab_project_id': 10002, 'name': 'c2'}]
    assert legacy == [
        {'_id': 'c3' * 12, 'gitlab_project_id': 10003, 'name': 'c3'},
        {'_id': 'c4' * 12, 'gitlab_project_id': 10004, 'name': 'c4'}]


def test_get_legacy_and_updated_components_with_lastest_and_base_release_and_different_components(monkeypatch):
    task = {'_id': 't1' * 12, 'args': {'release_id': 'a' * 24}}
    components = [
        {'_id': 'c1' * 12, 'gitlab_project_id': 10001, 'name': 'c1'},
        {'_id': 'c2' * 12, 'gitlab_project_id': 10002, 'name': 'c2'},
        {'_id': 'c3' * 12, 'gitlab_project_id': 10003, 'name': 'c3'},
        {'_id': 'c4' * 12, 'gitlab_project_id': 10004, 'name': 'c4'},
        {'_id': 'c5' * 12, 'gitlab_project_id': 10005, 'name': 'c5'}]  # new component

    release = {
        'name': 'v2.3.1',
        'branch': 'release_20181212_utest',
        'base_version': 'v2.3.0',
        'product': 'p' * 24,
        'features': ['f1' * 12, 'f2' * 12]}
    base_release = {
        'name': 'v2.3.0',
        'branch': 'release_20181111_utest',
        'product': 'p' * 24,
        'features': ['f0' * 12],
        'publish': {
            "by": "ci",
            "at": 1543922987726,
            "components": [
                {
                    '_id': 'c1' * 12,
                    'name': 'c1',
                    'type': 'app',
                    'docker_repo': 'docker-c1',
                    'version': 'v2.3.0'
                },
                {
                    '_id': 'c2' * 12,
                    'name': 'c2',
                    'type': 'app',
                    'docker_repo': 'docker-c2',
                    'version': 'v2.3.0'
                },
                {
                    '_id': 'c3' * 12,
                    'name': 'c3',
                    'type': 'app',
                    'docker_repo': 'docker-c3',
                    'version': 'v2.3.0'
                },
                {
                    '_id': 'c4' * 12,  # removed component in current product
                    'name': 'c4',
                    'type': 'sql',
                    'docker_repo': '',
                    'version': 'v2.3.0'
                },
            ]}}

    async def _mock_product_find_one(filter_):
        return {
            'components': ['c1' * 12, 'c2' * 12, 'c3' * 12, 'c5' * 12]}

    def _mock_feature_find(filter_):
        return AIterList([
            {
                '_id': 'f1' * 12,
                'components': ['c1' * 12]},
            {
                '_id': 'f2' * 12,
                'components': ['c1' * 12, 'c2' * 12]}])

    def _mock_component_find(filter_):
        return AIterList([c for c in components if c['_id'] in filter_['_id']['$in']])

    monkeypatch.setattr(Product, 'find_one', _mock_product_find_one)
    monkeypatch.setattr(Feature, 'find', _mock_feature_find)
    monkeypatch.setattr(Component, 'find', _mock_component_find)

    updated, legacy = read_async_result(_PublishTaskHandler(task)._get_updated_and_legacy_components(release, base_release, True))
    assert updated == [
        {'_id': 'c1' * 12, 'gitlab_project_id': 10001, 'name': 'c1'},
        {'_id': 'c2' * 12, 'gitlab_project_id': 10002, 'name': 'c2'}]
    assert legacy == [
        {'_id': 'c3' * 12, 'gitlab_project_id': 10003, 'name': 'c3'},
        {'_id': 'c5' * 12, 'gitlab_project_id': 10005, 'name': 'c5'}]

    updated, legacy = read_async_result(_PublishTaskHandler(task)._get_updated_and_legacy_components(release, base_release, False))
    assert updated == [
        {'_id': 'c1' * 12, 'gitlab_project_id': 10001, 'name': 'c1'},
        {'_id': 'c2' * 12, 'gitlab_project_id': 10002, 'name': 'c2'}]
    assert legacy == [
        {'_id': 'c3' * 12, 'gitlab_project_id': 10003, 'name': 'c3'},
        {'_id': 'c4' * 12, 'gitlab_project_id': 10004, 'name': 'c4'}]


def test_get_tag_commit_id(monkeypatch):
    task = {'_id': 't1' * 12, 'args': {'release_id': 'a' * 24}}

    async def _mock_get_projects_merge_requests(project_id, source_branch, target_branch, state):
        return [{
            'id': 1471,
            'iid': 61,
            'project_id': 33,
            'title': 'v2.3.2一些小修改',
            'description': '',
            'state': 'merged',
            'created_at': '2018-11-20T15:24:40.572+08:00',
            'updated_at': '2018-11-20T19:55:41.603+08:00',
            'merged_at': '2018-11-20T19:55:41.702+08:00',
            'closed_by': None,
            'closed_at': None,
            'target_branch': 'master',
            'source_branch': 'feature_hotfix_20181119_from_master',
            'upvotes': 0,
            'downvotes': 0,
            'source_project_id': 33,
            'target_project_id': 33,
            'labels': [],
            'work_in_progress': False,
            'milestone': None,
            'merge_when_pipeline_succeeds': False,
            'merge_status': 'can_be_merged',
            'sha': '48ea04e141e3debff1542a1f4e88ef55ffc03a76',
            'merge_commit_sha': '75e5c2eb72b8cdb41027f5fa32fda6225116d5c6',
            'user_notes_count': 0,
            'discussion_locked': None,
            'should_remove_source_branch': None,
            'force_remove_source_branch': True,
            'web_url': 'https://dev.dingxiang-inc.com:2020/ctu-group/ctu-engine/merge_requests/61',
            'squash': False}]

    async def _mock_get_branch_detail(project_id, source_branch):
        return {
            'name': 'release_20181119_monthly',
            'commit': {
                'id': '92eac7b5b0a3a700b4dd7a16245ad9d2bea0fd8d',
                'short_id': '92eac7b5',
                'title': '写es日志调整, 增加超时及异常处理, 缓存队列大小修改',
                'created_at': '2018-12-13T06:40:11.000Z',
                'parent_ids': ['af7c24aca87def1018d55b42ddfac99c3636b9d3'],
                'message': '写es日志调整, 增加超时及异常处理, 缓存队列大小修改\n',
                'author_name': 'jiangqian',
                'author_email': 'qian.jiang@dingxiang-inc.com',
                'authored_date': '2018-12-13T06:40:11.000Z',
                'committer_name': 'jiangqian',
                'committer_email': 'qian.jiang@dingxiang-inc.com',
                'committed_date': '2018-12-13T06:40:11.000Z'},
            'merged': False,
            'protected': False,
            'developers_can_push': False,
            'developers_can_merge': False,
            'can_push': True,
            'default': False}

    monkeypatch.setattr(GitlabApiWrapper, 'get_projects_merge_requests', _mock_get_projects_merge_requests)
    monkeypatch.setattr(GitlabApiWrapper, 'get_branch_detail', _mock_get_branch_detail)

    commit = read_async_result(_PublishTaskHandler(task)._get_tag_commit_id(33, 'feature_hotfix_20181119_from_master', 'master', 'ctu-engine', True))
    assert commit == '75e5c2eb72b8cdb41027f5fa32fda6225116d5c6'

    commit = read_async_result(_PublishTaskHandler(task)._get_tag_commit_id(33, 'release_20181119_monthly', 'master', 'ctu-engine', False))
    assert commit == '92eac7b5b0a3a700b4dd7a16245ad9d2bea0fd8d'


def test_get_tag_commit_id_without_merge_sha(monkeypatch):
    task = {'_id': 't1' * 12, 'args': {'release_id': 'a' * 24}}

    async def _mock_get_projects_merge_requests(project_id, source_branch, target_branch, state):
        return [{
            'id': 1471,
            'iid': 61,
            'project_id': 33,
            'title': 'v2.3.2一些小修改',
            'description': '',
            'state': 'merged',
            'closed_by': None,
            'closed_at': None,
            'target_branch': 'master',
            'source_branch': 'feature_hotfix_20181119_from_master',
            'upvotes': 0,
            'downvotes': 0,
            'source_project_id': 33,
            'target_project_id': 33,
            'labels': [],
            'work_in_progress': False,
            'milestone': None,
            'merge_when_pipeline_succeeds': False,
            'merge_status': 'can_be_merged',
            'sha': '48ea04e141e3debff1542a1f4e88ef55ffc03a76',
            'merge_commit_sha': None,
            'user_notes_count': 0,
            'discussion_locked': None,
            'should_remove_source_branch': None,
            'force_remove_source_branch': True,
            'web_url': 'https://dev.dingxiang-inc.com:2020/ctu-group/ctu-engine/merge_requests/61',
            'squash': False}]
    monkeypatch.setattr(GitlabApiWrapper, 'get_projects_merge_requests', _mock_get_projects_merge_requests)

    commit = read_async_result(_PublishTaskHandler(task)._get_tag_commit_id(33, 'feature_hotfix_20181119_from_master', 'master', 'ctu-engine', True))
    assert commit == '48ea04e141e3debff1542a1f4e88ef55ffc03a76'


def test_wait_until_tag_pipelines_success_success(monkeypatch):
    release_name = 'v2.3.0'
    components = [
        {'name': 'utest', 'gitlab_project_id': 1000001},
        {'name': 'utest2', 'gitlab_project_id': 1000002}]

    counter = {'cnt': 0}

    def _pipeline_gen():
        yield []
        counter['cnt'] += 1
        yield [{
            'id': 16327,
            'sha': 'a032b18f9a064be823eb5cfe47e42a12e6b46b36',
            'ref': 'v2.3.0',
            'status': 'pending',
            'web_url': 'https://dev.dingxiang-inc.com:2020/ctu-group/ctu-engine/pipelines/16327'}]
        counter['cnt'] += 1
        yield [{
            'id': 16327,
            'sha': 'a032b18f9a064be823eb5cfe47e42a12e6b46b36',
            'ref': 'v2.3.0',
            'status': 'running',
            'web_url': 'https://dev.dingxiang-inc.com:2020/ctu-group/ctu-engine/pipelines/16327'}]
        counter['cnt'] += 1
        yield [{
            'id': 16327,
            'sha': 'a032b18f9a064be823eb5cfe47e42a12e6b46b36',
            'ref': 'v2.3.0',
            'status': 'success',
            'web_url': 'https://dev.dingxiang-inc.com:2020/ctu-group/ctu-engine/pipelines/16327'}]
        counter['cnt'] += 1
        yield [{
            'id': 16327,
            'sha': 'a032b18f9a064be823eb5cfe47e42a12e6b46b36',
            'ref': 'v2.3.0',
            'status': 'success',
            'web_url': 'https://dev.dingxiang-inc.com:2020/ctu-group/ctu-engine/pipelines/16327'}]

    gen = _pipeline_gen()

    async def _mock_get_projects_pipelines(**kwargs):
        return next(gen)

    monkeypatch.setattr(GitlabApiWrapper, 'get_projects_pipelines', _mock_get_projects_pipelines)
    read_async_result(_PublishTaskHandler({'_id': 0, 'args': {}})._wait_until_tag_pipelines_success(release_name, components))
    assert counter['cnt'] == 4


def test_wait_until_tag_pipelines_success_failed(monkeypatch):
    release_name = 'v2.3.0'
    components = [{'name': 'utest', 'gitlab_project_id': 1000001}]

    counter = {'cnt': 0}

    def _pipeline_gen():
        yield []
        counter['cnt'] += 1
        yield [{
            'id': 16327,
            'sha': 'a032b18f9a064be823eb5cfe47e42a12e6b46b36',
            'ref': 'v2.3.0',
            'status': 'pending',
            'web_url': 'https://dev.dingxiang-inc.com:2020/ctu-group/ctu-engine/pipelines/16327'}]
        counter['cnt'] += 1
        yield [{
            'id': 16327,
            'sha': 'a032b18f9a064be823eb5cfe47e42a12e6b46b36',
            'ref': 'v2.3.0',
            'status': 'running',
            'web_url': 'https://dev.dingxiang-inc.com:2020/ctu-group/ctu-engine/pipelines/16327'}]
        counter['cnt'] += 1
        yield [{
            'id': 16327,
            'sha': 'a032b18f9a064be823eb5cfe47e42a12e6b46b36',
            'ref': 'v2.3.0',
            'status': 'failed',
            'web_url': 'https://dev.dingxiang-inc.com:2020/ctu-group/ctu-engine/pipelines/16327'}]

    gen = _pipeline_gen()

    async def _mock_get_projects_pipelines(**kwargs):
        return next(gen)

    monkeypatch.setattr(GitlabApiWrapper, 'get_projects_pipelines', _mock_get_projects_pipelines)
    with pytest.raises(TaskFailed):
        read_async_result(_PublishTaskHandler({'_id': 0, 'args': {}})._wait_until_tag_pipelines_success(release_name, components))
    assert counter['cnt'] == 3


def test_get_latest_release(monkeypatch):
    def _mock_release_find(filter_, fields):
        return AIterList([
            {'name': 'v2.3.9'},
            {'name': 'v2.3.8'},
            {'name': 'v2.3.7'},
            {'name': 'v2.3.6'},
            {'name': 'v2.3.5'},
            {'name': 'v2.3.4'},
            {'name': 'v2.3.3'},
            {'name': 'v2.3.2'},
            {'name': 'v2.3.10'},
            {'name': 'v2.3.1'},
            {'name': 'v2.3.0'},
            {'name': 'v2.2.6'},
            {'name': 'v2.2.5'},
            {'name': 'v2.2.4'},
            {'name': 'v2.2.3'},
            {'name': 'v2.2.2'},
            {'name': 'v2.2.1'},
            {'name': 'v2.2.0'},
        ])
    monkeypatch.setattr(Release, 'find', _mock_release_find)
    assert read_async_result(_PublishTaskHandler({'_id': 0, 'args': {}})._get_latest_release('p' * 24)) == 'v2.3.10'


def test_can_do_publish(monkeypatch):
    async def _empty_mrs(project_id, source_branch, target_branch):
        return []

    monkeypatch.setattr(GitlabApiWrapper, 'get_projects_merge_requests', _empty_mrs)
    with pytest.raises(TaskFailed):
        read_async_result(_PublishTaskHandler({'_id': 0, 'args': {}})._can_do_publish(True, 'test_release', [{'gitlab_project_id': 123, 'name': 'test'}]))

    async def _closed_mrs(project_id, source_branch, target_branch):
        return [{
            'id': 1471,
            'iid': 61,
            'project_id': 33,
            'state': 'closed',
            'squash': False}]

    monkeypatch.setattr(GitlabApiWrapper, 'get_projects_merge_requests', _closed_mrs)
    with pytest.raises(TaskFailed):
        read_async_result(_PublishTaskHandler({'_id': 0, 'args': {}})._can_do_publish(True, 'test_release', [{'gitlab_project_id': 123, 'name': 'test'}]))

    async def _no_upvotes_mrs(project_id, source_branch, target_branch):
        return [{
            'id': 1471,
            'iid': 61,
            'project_id': 33,
            'state': 'open',
            'upvotes': 0,
            'downvotes': 1,
            'squash': False}]

    monkeypatch.setattr(GitlabApiWrapper, 'get_projects_merge_requests', _no_upvotes_mrs)
    with pytest.raises(TaskFailed):
        read_async_result(_PublishTaskHandler({'_id': 0, 'args': {}})._can_do_publish(True, 'test_release', [{'gitlab_project_id': 123, 'name': 'test'}]))

    async def _cannot_merge(project_id, source_branch, target_branch):
        return [{
            'id': 1471,
            'iid': 61,
            'project_id': 33,
            'state': 'open',
            'merge_status': 'cannot_be_merged',
            'upvotes': 1,
            'downvotes': 0,
            'squash': False}]

    monkeypatch.setattr(GitlabApiWrapper, 'get_projects_merge_requests', _cannot_merge)
    with pytest.raises(TaskFailed):
        read_async_result(_PublishTaskHandler({'_id': 0, 'args': {}})._can_do_publish(True, 'test_release', [{'gitlab_project_id': 123, 'name': 'test'}]))

    async def _valid_mr(project_id, source_branch, target_branch):
        return [{
            'id': 1471,
            'iid': 61,
            'project_id': 33,
            'state': 'open',
            'merge_status': 'can_be_merged',
            'upvotes': 1,
            'downvotes': 0,
            'squash': False}]

    monkeypatch.setattr(GitlabApiWrapper, 'get_projects_merge_requests', _valid_mr)
    read_async_result(_PublishTaskHandler({'_id': 0, 'args': {}})._can_do_publish(True, 'test_release', [{'gitlab_project_id': 123, 'name': 'test'}]))
