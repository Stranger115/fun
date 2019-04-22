import logging
from sanic import Blueprint
from sanic.response import json
from sanic.exceptions import InvalidUsage, NotFound
from tao.models.product import Product, Label, Order, ShoppingCart
from tao.settings import PRODUCTS_LINE_LIMIT
from tao.utils import jsonify
from bson.objectid import ObjectId


product_bp = Blueprint('product')


@product_bp.get('/api/v1/products')
async def get_products(request):
    """获取商品列表"""
    results = [record async for record in Product.find({})]
    products = []
    for i in range(0, len(results), PRODUCTS_LINE_LIMIT):
        products.append(results[i:i + PRODUCTS_LINE_LIMIT])
    return json(jsonify(products))


@product_bp.get('/api/v1/all_products')
async def get_all_products(request):
    """获取所有商品列表"""
    products = [record async for record in Product.find({})]
    for i in products:
        label = await Label.find_one({'_id': ObjectId(i.get('label', None))})
        i.update({'label': label['name']})
    return json(jsonify({'products': products, 'total': await Product.count_documents({})}))


@product_bp.post('/api/v1/order/<user_id>')
async def post_order(request, user_id):
    """提交商品订单"""
    if request.json:
        raise InvalidUsage('not json request!')
    product = request.json.get('product')
    num = request.json.get('num')
    user_id = user_id
    order = await ShoppingCart.create(product, user_id, num)
    return json(jsonify({'id': order.inserted_id}))


@product_bp.put('/api/v1/loadProduct/<name>')
async def update_product(request, name):
    """商品上下架"""
    flag = request.json.get('flag')
    await Product.update_one({'name': name}, {'$set': {'flag': flag}})
    return json(jsonify({'_id': id}))


@product_bp.put('/api/v1/product/<id>')
async def update_product(request, id):
    """商品更新"""
    if request.json:
        raise InvalidUsage('not json request!')
    name = request.json.get('name')
    stock = request.json.get('stock')
    price = request.json.get('price')
    label = request.json.get('label')
    product = await Product.update_one(
        {'_id': id},
        {'$set':
         {
             'name': name,
             'stock': stock,
             'price': price,
             'label': label
         }
         }
    )
    return json(jsonify({'id': product.inserted_id}))


@product_bp.post('/api/v1/product')
async def post_product(request):
    """商品录入"""
    if not request.json:
        raise InvalidUsage('not json request!')
    name = request.json.get('name')
    stock = request.json.get('stock')
    price = request.json.get('price')
    label = request.json.get('label')
    product = await Product.create(name, stock, price, label)
    return json(jsonify({'id': product.inserted_id}))


@product_bp.get('/api/v1/labels')
async def get_label(request):
    """获取商品类型"""
    labels = [record async for record in Label.find({})]
    return json(jsonify({'labels': labels}))


@product_bp.post('api/v1/label')
async def add_label(request):
    """添加商品类型"""
    name = request.json.get('name')
    # await Label.delete_many({'name': name})
    result = await Label.find_one({'name': name})
    logging.info(result)
    logging.info(not result)
    if not result:
        await Label.create(name)
        return json(jsonify({'result': 'success'}))
    raise InvalidUsage('分类已存在')
