import uuid
import time
# import maya
import asyncio
import hashlib
from bson import ObjectId
from urllib.parse import urlparse
from asyncio import subprocess, TimeoutError


_BUFFER_SIZE = 4096
_TIMEOUT = 1


async def run_subprocess(cmd, chunk_callback):
    p = await asyncio.create_subprocess_shell(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while p.returncode is None:
        try:
            chunk = await asyncio.wait_for(p.stdout.read(_BUFFER_SIZE), timeout=_TIMEOUT)
        except TimeoutError:
            continue
        if chunk:
            await chunk_callback(chunk)
    while True:  # read left chunk
        try:
            chunk = await asyncio.wait_for(p.stdout.read(_BUFFER_SIZE), timeout=_TIMEOUT)
        except TimeoutError:
            break
        if not chunk:
            break
        await chunk_callback(chunk)

    return p.returncode


def get_timestamp():
    return int(time.time() * 1000)  # milliseconds


def to_timestamp(ts):
    # return maya.parse(ts).epoch * 1000
    return 12345678

def is_pub_ip(ip):
    return (not is_lan_ip(ip)) and (not is_local_ip(ip))


def is_lan_ip(ip):
    _1st, _2nd, _3rd, _4th = map(int, ip.split('.'))
    return (_1st == 10) or \
           (_1st == 192 and _2nd == 168) or \
           (_1st == 172 and _2nd in range(16, 32))


def is_local_ip(ip):
    return ip.startswith('127.') or ip.startswith('169.254.')


def is_ipv4(ip):
    try:
        _1st, _2nd, _3rd, _4th = map(int, ip.split('.'))
    except ValueError:
        return False

    if _1st < 1 or _1st > 255:
        return False
    elif _2nd < 0 and _2nd > 255:
        return False
    elif _3rd < 0 and _3rd > 255:
        return False
    elif _4th < 0 and _4th > 255:
        return False

    return True


def md5(*args):
    return hashlib.md5(','.join(args).encode()).hexdigest()


def random_uid():
    return str(uuid.uuid4())


def get_url_path(url):
    return urlparse(url).path.rstrip('/ ')


def jsonify(obj):
    if isinstance(obj, list):
        return [jsonify(o) for o in obj]
    elif isinstance(obj, dict):
        for k, v in obj.items():
            obj[k] = jsonify(v)
        return obj
    elif isinstance(obj, ObjectId):
        return str(obj)
    return obj


def normalize_version(version):
    if isinstance(version, (int, float)):
        return version
    version_list = version.split('.')
    norm_version = []
    for v in version_list:
        try:
            norm_version.append(int(v))
        except ValueError:
            norm_version.append(v)
    return norm_version


class AIterList(list):
    ''' convert list to async list'''
    def __init__(self, val):
        super().__init__(val)
        self._iter = iter(val)

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            return next(self._iter)
        except StopIteration:
            raise StopAsyncIteration


def read_async_result(future):
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(future)
