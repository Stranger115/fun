#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# _author: Stranger
# date: 2019/4/20

import hashlib
import logging
from sanic import Blueprint
from functools import reduce
from sanic.response import json
from sanic.exceptions import InvalidUsage, ServerError
from tao.models import AllUser, Permission
from tao.utils import jsonify


role_bp = Blueprint('role')
per_dict = {1: '商品购买', 2: '账单管理', 4: '会员管理', 8: '权限管理', 16: '商品管理'}


@role_bp.post('api/v1/change_user_role')
async def change_user(request):
    result = AllUser.find_one({})
    return json(jsonify({'success': '成功'}))


@role_bp.post('api/v1/add_role')
async def add_role(request):
    """添加会员等级"""
    role = request.json.get('role')
    des = request.json.get('description')
    level = request.json.get('level')
    permission = request.json.get('permission', [])
    logging.info(f'------{role}的功能权限列表:{permission}------')

    result = await Permission.find_one({'role': role})
    if not result:
        per = Permission()
        per.role = role
        per.description = des
        per.permission = permission
        per.order = 1
        per.level = level
        await per.save()
        return json(jsonify({'success': 1}))
    return InvalidUsage('会员等级已存在')


@role_bp.put('api/v1/role')
async def update_role(request):
    role = request.json.get('role')
    permission = request.json.get('permission')
    logging.info(f'----{role}更新权限：{permission}-------')
    try:
        result = await Permission.find_one_and_update({'role': role},
                                         {'$set': {'permission': permission}})
        return json(jsonify({'success': 1}))
    except Exception as e:
        logging.info(f'----{e}-----')
        raise ServerError('系统错误')


@role_bp.get('api/v1/roles')
async def get_roles(request):
    roles = [record async for record in Permission.find({})]
    for record in roles:
        per_text = [per_dict[i] for i in record['permission']]
        record['permission'] = per_text
    return json(jsonify({
        'total': await Permission.count_documents({}),
        'roles': roles}))

