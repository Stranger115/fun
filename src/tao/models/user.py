from .base import BaseModel


class User(BaseModel):
    __cname__ = 'user'

    @classmethod
    def create(cls, user_name, password, picture, sex, birthday, role, money):
        return cls.create({
            'user_name': user_name,
            'password': password,
            'picture': picture,
            'sex': sex,
            'birthday': birthday,
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