import pymongo
from .base import BaseModel



class AllUser(BaseModel):
    __cname__ = 'user'
    __indexes__ = [
        {'indexes': [
            ('user_name', pymongo.ASCENDING)],
            'unique': True}]

    @classmethod
    def create(cls, user_name, password,  sex, picture=None, role=0, money=0):
        return cls.create({
            'user_name': user_name,
            'password': password,
            'picture': picture,
            'sex': sex,
            'user_label': role,
            'money': money
        })


class Permission(BaseModel):
    __cname__ = 'permission'

    @classmethod
    def create(cls, role):
        return cls.create({
            'role': role
        })