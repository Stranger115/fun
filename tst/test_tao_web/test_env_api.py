import ujson
from bson import ObjectId
from sanic.exceptions import SanicException
from tao.models import Environment
from tao.web.api.common import reserve_environment, free_environment
from test_common import MockRequest
from tao.utils import read_async_result


envs = [
    {'_id': ObjectId('1'*24), 'status': Environment.IDLE, 'ip': '1.1.1.1', 'name': 'test-1'},
    {'_id': ObjectId('2'*24), 'status': Environment.IDLE, 'ip': '2.2.2.2', 'name': 'test-2'} ]


def test_reserve_env(monkeypatch):
    async def _mock_update(filter_, set_, **kwargs):
        def _match(env, sk, sv):
            if '.' in sk:
                p, c = sk.split('.')
                if env.setdefault(p, {}).get(c) != sv:
                    return False
            else:
                if env[sk] != sv:
                    return False
            return True

        def _get_env(filter_):
            for env in envs:
                if '$or' not in filter_:
                    for k, v in filter_.items():
                        if not _match(env, k, v):
                            break
                    else:
                        return env

                else:
                    for sub_filter in filter_['$or']:
                        for sk, sv in sub_filter.items():
                            if not _match(env, sk, sv):
                                break
                        else:
                            return env

            return None

        env = _get_env(filter_)

        if not env:
            return env

        env.update(set_['$set'])
        return env

    monkeypatch.setattr(Environment, 'find_one_and_update', _mock_update)

    def _reserve_env(assign_type, assign_id, product_id, duration):
        request = MockRequest(
                assign_type=assign_type,
                assign_id=assign_id,
                product_id=product_id,
                duration=duration)
        try:
            resp = read_async_result(reserve_environment(request))
            return ujson.loads(resp.body)
        except SanicException as err:
            return err.status_code

    assert _reserve_env('test', '123', 'p1', 0.1)['ip'] == '1.1.1.1'  # reserve free env
    assert _reserve_env('test', '124', 'p1', 0.1)['ip'] == '2.2.2.2'  # reserve another one
    assert _reserve_env('test', '125', 'p1', 0.1) == 404  # no available env
    assert _reserve_env('test', '123', 'p1', 0.1)['ip'] == '1.1.1.1'  # can increase expire time
    read_async_result(free_environment(MockRequest(
        assign_type='test',
        assign_id='125',
        ip='1.1.1.1')))
    assert _reserve_env('test2', '125', 'p1', 0.1) == 404
    read_async_result(free_environment(MockRequest(
        assign_type='test',
        assign_id='123',
        ip='1.1.1.1')))
    assert _reserve_env('test2', '125', 'p1', 0.1)['ip'] == '1.1.1.1'
