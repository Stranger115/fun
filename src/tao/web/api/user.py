import hashlib
from sanic import Blueprint
from sanic_auth import Auth, User
from sanic.response import json
from tao.web.__main__ import auth
from tao.models import User
from tao.utils import jsonify


user_bp = Blueprint('user')


@user_bp.post('/api/v1/regedit')
async def regedit(request):
    """注册"""
    user_name = request.json.get('name')
    psd = request.json.get('password')
    picture = request.json.get('picture')
    sex = request.json.get('sex')
    birthday = request.json.get('birthday')
    role = request.json.get('role')
    money = request.json.get('money')
    result = await User.find({'user_name': user_name})
    secret = hashlib.md5(psd)
    if result:
        user = await User.create(user_name, secret, picture, sex, birthday, role, money)
        return json(jsonify({'id': user.inserted_id}))
    return json(jsonify({'error': '用户已存在'}))


@user_bp.post('/api/v1/login')
async def login(request):
    """登录"""
    user_name = request.json.get('name')
    psd = request.json.get('password')
    result = User.find_one({'user_name': user_name})
    # 密码加密
    if result['password'] == hashlib.md5(psd):
        return json(jsonify({'success': '登录成功'}))
    return json(jsonify({'error': '用户已存在'}))


@user_bp.post('api/v1/change_profile')
async def change_profile(request):
    """修改个人资料"""

