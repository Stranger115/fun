#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# _author: Stranger
# date: 2019/4/20

import hashlib
import logging
from sanic import Blueprint
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
    pass


@role_bp.get('api/v1/roles')
async def get_roles(request):
    skip = int(request.args.get('skip', 0))
    limit = int(request.args.get('limit', 10))
    filter_ = {}
    q_ = request.args.get('q')
    if q_:
        filter_['$or'] = [
            {'fqdn': {'$regex': '(?i)' + q_}},
            {'ip': {'$regex': q_}}]
    return json(jsonify({
        'total': await Permission.count_documents(filter_),
        'role': [record async for record in
                Permission.find(filter_, skip=skip,
                         limit=limit)]}))

