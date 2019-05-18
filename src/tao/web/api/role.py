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
    per = request.json.get('permission', [])
    logging.info(f'------{role}的功能权限列表:{per}------')
    permission = reduce(lambda x, y: x+y, per) if level == 1 else 0x03

    result = await Permission.find_one({'role': role})
    if not result:
        per = Permission()
        per.role = role
        per.description = des
        per.permission = permission
        per.order = 1
        await per.save()
        return json(jsonify({'success': 1}))
    return InvalidUsage('会员等级已存在')


@role_bp.get('api/v1/roles')
async def get_roles(request):
    return json(jsonify({
        'total': await Permission.count_documents({}),
        'role': [record async for record in
                Permission.find({})]}))

