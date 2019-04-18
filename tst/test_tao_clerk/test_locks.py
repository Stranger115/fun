from tao.clerk.locks import acquire_lock, release_lock
from tao.utils import read_async_result


def test_lock():
    assert read_async_result(acquire_lock('resource-a')) is not None
    assert read_async_result(acquire_lock('resource-a')) is None

    release_lock('resource-a')
    assert read_async_result(acquire_lock('resource-a')) is not None
    assert read_async_result(acquire_lock('resource-b')) is not None
