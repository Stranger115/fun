from tao.models import BaseModel,AllUser
from tao.utils import read_async_result, AIterList


class _MockDB(object):
    def __getattr__(self, attr):
        return _MockCollection(attr)


class _MockCollection(object):
    def __init__(self, name):
        self.name = name

    def __getattr__(self, attr):
        async def _mock_function(*args, **kwargs):
            return [e async for e in AIterList([self.name])]
        return _mock_function


def test_common_operations(monkeypatch):
    monkeypatch.setattr(BaseModel, '__db__', _MockDB())
    read_async_result(AllUser.update_many({}, {'$set': {'done': True}}))
