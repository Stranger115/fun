import hashlib
import logging
from sanic import Blueprint
from sanic.response import json
from sanic.exceptions import InvalidUsage, ServerError
from tao.models import AllUser
from tao.utils import jsonify


user_bp = Blueprint('users')
md5 = hashlib.md5()


@user_bp.post('/api/v1/regedit')
async def regedit(request):
    """注册"""
    # await AllUser.delete_many({})
    user_name = request.json.get('username')
    psd = request.json.get('password')
    sex = request.json.get('sex')
    try:
        result = await AllUser.find_one({'user_name': user_name})
        if not result:
            md5.update(psd.encode("utf8"))
            secret = md5.hexdigest()
            user = AllUser()
            user.user_name = user_name
            user.password = secret,
            user.sex = sex
            result = await user.save()
            logging.info(result)
            return json(jsonify({'success': '注册成功'}))
        else:
            raise InvalidUsage('用户已存在')
    except Exception as e:
        logging.info(e)



@user_bp.post('/api/v1/login')
async def login(request):
    """登录"""
    user_name = request.json.get('name')
    psd = request.json.get('password')
    result = AllUser.find_one({'user_name': user_name})
    # 密码加密
    if result['password'] == hashlib.md5(psd):
        return json(jsonify({'success': '登录成功'}))
    return json(jsonify({'error': '用户已存在'}))


@user_bp.post('api/v1/change_profile')
async def change_profile(request):
    """修改个人资料"""

