import hashlib
import logging
from sanic import Blueprint
from sanic.response import json
from sanic.exceptions import InvalidUsage, ServerError
from tao.models import AllUser, Permission
from tao.utils import jsonify
from bson import ObjectId


user_bp = Blueprint('users')


def hash_psd(psd):
    md5 = hashlib.md5()
    md5.update(psd.encode("utf8"))
    secret = md5.hexdigest()
    return secret


@user_bp.post('/api/v1/regedit')
async def regedit(request):
    """注册"""
    user_name = request.json.get('username')
    psd = request.json.get('password')
    phone = request.json.get('phone')
    sex = request.json.get('sex')
    try:
        result = await AllUser.find_one({'user_name': user_name})
        if not result:
            # 对密码进行加密处理
            secret = hash_psd(psd)
            # 数据存储
            user = AllUser()
            user.user_name = user_name
            user.password = secret
            user.phone = phone
            user.sex = sex
            user.role = 0xff
            await user.save()
            # await AllUser.create('user',
            #     {'user_name': user_name,
            #      'password': secret,
            #      'phone': phone,
            #      'sex': sex,
            #      'role': 0xff
            #      })
            logging.info(result)
            return json(jsonify({'success': '注册成功'}))
        else:
            raise InvalidUsage('用户已存在')
    except Exception as e:
        logging.info(e)
        raise InvalidUsage('系统错误')


@user_bp.post('/api/v1/login')
async def login(request):
    """登录"""
    user_name = request.json.get('username')
    psd = request.json.get('password')
    result = await AllUser.find_one({'user_name': user_name})
    # 密码加密
    if result:
        secret = hash_psd(psd)
        if result['password'][0] == secret:
            return json(jsonify({'username': user_name, 'role': result.get('user_label', 0)}))
        else:
            raise InvalidUsage('密码或用户名错误')
    raise InvalidUsage('用户不存在')


@user_bp.post('api/v1/change_profile')
async def change_profile(request):
    """修改个人资料"""


@user_bp.get('api/v1/users')
async def get_user(request):
    result = [user async for user in AllUser.find({})]
    users = []
    for record in result:
        role = record.get('user_label', 0)
        role_des = await Permission.find_one({'role': role})
        user = {
            '_id':record.get('_id', None),
            'username': record.get('user_name', '未命名'),
            'phone': record.get('phone', ''),
            'role':  '普通会员',
            'sex': record.get('sex', 1)
        }
        users.append(user)
    return json(jsonify({'users': users, 'total': await AllUser.count_documents({})}))


@user_bp.put('api/v1/user')
async def change_user(request):
    id_ = request.json.get('_id')

    user_name = request.json.get('username')
    psd = request.json.get('phone')
    sex = request.json.get('sex')
    role = request.json.get('role')

    if not id_:
        raise InvalidUsage('无效的请求参数！')

    fqdn = request.json.get('fqdn', '').strip()
    ip = request.json.get('ip', '').strip()
    #

    return json({})


@user_bp.put('api/v1/add_user')
async def add_user(request):
    """管理员添加用户"""
    user_name = request.json.get('username')
    psd = request.json.get('phoneNum')
    sex = request.json.get('sex')
    role = request.json.get('role')
    try:
        result = await AllUser.find_one({'user_name': user_name})
        if not result:
            secret = hash_psd(psd)
            logging.info(secret)
            user = AllUser()
            user.user_name = user_name
            user.phone = psd
            user.password = secret,
            user.sex = sex
            result = await user.save()
            logging.info(result)
            return json(jsonify({'success': '注册成功'}))
        else:
            raise InvalidUsage('用户已存在')
    except Exception as e:
        logging.info(e)


