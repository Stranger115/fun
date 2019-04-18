from tao.web.hooks.cci_handler import trigger_dependent_cci, Task
from tao.utils import read_async_result


def test_trigger_cci(monkeypatch):
    tasks = []

    class _Task(object):
        def __init__(self, id_):
            self.inserted_id = id_

    async def _mock_task_create(name, args, trigger_by):
        tasks.append({
            'name': name,
            'args': args,
            'trigger_by': trigger_by})
        return _Task('a' * 24)

    monkeypatch.setattr(Task, 'create', _mock_task_create)
    event = {
        'object_kind': 'pipeline',
        'object_attributes': {
            'id': 10145,
            'ref': 'master',
            'tag': False,
            'sha': '14f7ea23077d1310454a1cad835d8c0ba4028a58',
            'before_sha': '28da57f5a1fef14381a9bc753d52b701f3953aaf',
            'status': 'pending',
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
    read_async_result(trigger_dependent_cci(event))
    assert len(tasks) == 0

    event['object_attributes']['status'] = 'success'
    read_async_result(trigger_dependent_cci(event))
    assert len(tasks) == 1
    assert tasks[0]['name'] == 'trigger_cci'
    assert tasks[0]['args'] == {'namespace': 'aladdin', 'project': 'tao', 'project_id': 602, 'branch': 'master', 'owner': 10145}
    assert tasks[0]['trigger_by'] == 'zhangyu'

    event['object_attributes']['tag'] = True
    read_async_result(trigger_dependent_cci(event))
    assert len(tasks) == 1
