import asyncio
from bson import ObjectId
from tao.utils import run_subprocess, to_timestamp, get_url_path, jsonify, normalize_version


def run_async_func(future):
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(future)


def test_run_subprocess():
    ctx = {'output': b''}

    async def _callback(chunk):
        ctx['output'] += chunk
    run_async_func(run_subprocess('echo aaa', _callback))
    assert ctx['output'] == b'aaa\n'


def test_run_subprocess_with_error():
    ctx = {'output': b''}

    async def _callback(chunk):
        ctx['output'] += chunk
    run_async_func(run_subprocess('curl -m 0.1 http://invalid.invalidxxxx.ccn', _callback))
    assert ctx['output'] != b''


def test_run_subprocess_with_timeout():
    ctx = {'output': b''}

    async def _callback(chunk):
        ctx['output'] += chunk
    run_async_func(run_subprocess('ping -c 2 127.0.0.1', _callback))
    assert ctx['output'] != b''


def test_to_timestamp():
    assert to_timestamp('2016-08-12 15:23:28 UTC') == 1471015408000


def test_get_url_path():
    assert get_url_path('https://xxewr.wreqw.com/ctu-group/ctu-console') == '/ctu-group/ctu-console'
    assert get_url_path('https://xxewr.wreqw.com/ctu-group/ctu-console/') == '/ctu-group/ctu-console'
    assert get_url_path('http://xxewr.wreqw.com/ctu-group/ctu-console/ ') == '/ctu-group/ctu-console'


def test_jsonify():
    assert jsonify(ObjectId('1'*24)) == '1'*24
    assert jsonify({'name': 'hello', '_id': ObjectId('1'*24)}) == {'name': 'hello', '_id': '1'*24}
    assert jsonify(None) is None
    assert jsonify([
        {'name': 'hello', '_id': ObjectId('1'*24)},
        {'name': 'world', '_id': ObjectId('2'*24)}]) == [
                {'name': 'hello', '_id': '1'*24},
                {'name': 'world', '_id': '2'*24}]
    assert jsonify({'hello': {'world': ObjectId('1'*24)}}) == {'hello': {'world': '1'*24}}


def test_normalize_version():
    assert normalize_version(1) == 1
    assert normalize_version(1.0) == 1.0
    assert normalize_version('v2.3.4') == ['v2', 3, 4]
