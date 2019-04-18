import pymongo
from tao.utils import get_timestamp
from .base import BaseModel


class Product(BaseModel):
    __cname__ = 'product'
    __indexes__ = [
        {'indexes': [('name', pymongo.ASCENDING)], 'unique': True}]

    @classmethod
    async def create(cls, name, stock, price, label, flag=False):
        return await cls.insert_one({
            'name': name,
            'stock': stock,
            'price': price,
            'label': label,
            'flag': flag,
            'create_time': get_timestamp(),
            'update_time': get_timestamp()})


class ShoppingCart(BaseModel):
    __cname__ = 'shopping_cart'

    @classmethod
    async def create(cls, product, user_id, num):
        return await cls.insert_one({
            'product': product,
            'user_id': user_id,
            'num': num
        })


class Order(BaseModel):
    __cname__ = 'order'

    @classmethod
    async def create(cls, product, user_id, total):
        return await cls.insert_one({
            'product': product,
            'user_id': user_id,
            'total': total,
            'create_time': get_timestamp()
        })
