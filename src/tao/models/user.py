import pymongo
from .base import BaseModel
from tao.utils import get_timestamp


class AllUser(BaseModel):
    __cname__ = 'user'
    __indexes__ = [
        {'indexes': [
            ('user_name', pymongo.ASCENDING)],
            'unique': True}]

    @classmethod
    def create(cls, user_name, password, phone,  sex, picture=None, score=0, role=0x03, money=0):
        return cls.create({
            'user_name': user_name,
            'password': password,
            'phone': phone,
            'picture': picture,
            'score': score,
            'sex': sex,
            'user_label': role,
            'money': money,
            'create_time': get_timestamp(),
            'update_time': get_timestamp()
        })


class Permission(BaseModel):
    __cname__ = 'permission'
    __indexes__ = [
        {'indexes': [
            ('role', pymongo.ASCENDING)],
            'unique': True}]

    @classmethod
    def create(cls, role, description, order=1, level=0, permission=0x03):
        return cls.create({
            'role': role,
            'description': description,
            'order': order,
            'level': level,
            'permission': permission,
        })