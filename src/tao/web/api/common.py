import itertools
from sanic import Blueprint
from sanic.response import json
from sanic.exceptions import InvalidUsage, NotFound
from bson import ObjectId
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError
from tao.models import Task, Product, Release, Feature, Environment, Component, MergeRequest
from tao.utils import get_timestamp, jsonify
from tao.settings import SSH_USER, SSH_PASSWORD
from tao import __version__ as tao_version

common_bp = Blueprint('common')


@common_bp.get('/api/v1/version')
async def get_version(request):
    return json({'version': tao_version})


@common_bp.get('/api/v1/tasks')
async def get_tasks(request):
    skip = int(request.args.get('skip', 0))
    limit = int(request.args.get('limit', 10))
    q_ = request.args.get('q')
    if q_:
        f_ = {'$or': [
            {'trigger_by': {'$regex': '(?i)' + q_}},
            {'name': {'$regex': '(?i)' + q_}},
        ]}
        total = await Task.count_documents(f_)
    else:
        f_ = {}
        total = await Task.estimated_document_count()
    tasks = [
        task async for task in Task.find(
            f_, ['name', 'status', 'trigger_by', 'create_time', 'update_time'],
            sort=[('create_time', -1)],
            skip=skip,
            limit=limit)]
    return json(jsonify({'total': total, 'tasks': tasks}))


@common_bp.get('/api/v1/task/<task_id>')
async def get_task_detail(request, task_id):
    task = await Task.find_one({'_id': ObjectId(task_id)}) or {}
    task['logs'] = b''.join((isinstance(log, str) and log.encode() or log for log in task.get('logs', '')))
    return json(jsonify(task))


@common_bp.post('/api/v1/tasks')
async def new_task(request):
    if not request.json:
        raise InvalidUsage('not json request!')
    task_name = request.json.get('name')
    task_args = request.json.get('args')
    if not task_name:
        raise InvalidUsage('no name found!')
    trigger_by = request['session']['user']['username']
    task = await Task.create(task_name, task_args, trigger_by)
    return json(jsonify({'id': task.inserted_id}))


@common_bp.get('/api/v1/products')
async def get_products(request):
    async def _read_product_components(p):
        return [c async for c in Component.find(
            {'_id': {'$in': p['components']}})]

    async def _read_product_features(p):
        return {
            'total': await Feature.count_documents(
                {'product': p['_id'], 'status': Feature.DONE})}

    async def _read_product_releases(p):
        last_release = await Release.find_one(
            {'product': p['_id'], 'status': Release.RELEASED},
            sort=[('update_time', -1)])
        if last_release:
            last_release['features'] = [
                f async for f in Feature.find(
                    {'_id': {'$in': last_release['features']}}, ['name'])]
        return {
            'total': await Release.count_documents(
                {'product': p['_id'], 'status': Release.RELEASED}),
            'last': last_release}

    async def _read_product_environments(p):
        return {
            'total': await Environment.count_documents(
                {'assign_to.product': p['_id'], 'status': Environment.BUSY})}

    products = []
    id_ = request.args.get('id')
    format_ = request.args.get('format')
    if id_:
        filter_ = {'_id': ObjectId(id_)}
    else:
        filter_ = {}
    q_ = request.args.get('q')
    if q_:
        filter_['name'] = {'$regex': '(?i)' + q_}

    async for p in Product.find(filter_):
        if format_ != 'simple':
            p['components'] = await _read_product_components(p)
            p['features'] = await _read_product_features(p)
            p['releases'] = await _read_product_releases(p)
            p['environments'] = await _read_product_environments(p)
        products.append(p)

    return json(jsonify(products))


@common_bp.post('/api/v1/products')
async def new_product(request):
    name = request.json.get('name', '').strip()
    description = request.json.get('description', '').strip()
    components = [ObjectId(c) for c in request.json.get('components', [])]
    export_script = request.json.get('export_script', '').strip()
    deploy_script = request.json.get('deploy_script', '').strip()

    if not name:
        raise InvalidUsage('Product名称不能为空！')

    try:
        p = await Product.create(name, description, components, export_script, deploy_script)
    except DuplicateKeyError:
        raise InvalidUsage('同名Product已存在！')

    return json(jsonify({'id': p.inserted_id}))


@common_bp.put('/api/v1/products')
async def update_product(request):
    _id = request.json.get('_id')
    if not _id:
        raise InvalidUsage('无效的请求参数！')
    name = request.json.get('name', '').strip()
    description = request.json.get('description', '').strip()
    components = [ObjectId(c) for c in request.json.get('components', [])]
    export_script = request.json.get('export_script', '').strip()
    deploy_script = request.json.get('deploy_script', '').strip()
    if not name:
        raise InvalidUsage('Product名称不能为空！')
    await Product.find_one_and_update(
        {'_id': ObjectId(_id)},
        {'$set': {
            'name': name,
            'description': description,
            'components': components,
            'export_script': export_script,
            'deploy_script': deploy_script,
            'update_time': get_timestamp()}})

    return json({})


@common_bp.get('/api/v1/components')
async def get_components(request):
    q_ = request.args.get('q')
    if q_:
        f_ = {'name': {'$regex': '(?i)' + q_}}
    else:
        f_ = {}
    return json(jsonify([c async for c in Component.find(f_)]))


@common_bp.post('/api/v1/components')
async def new_component(request):
    name = request.json.get('name', '').strip()
    branch = request.json.get('master_name', '').strip()
    gitlab_project_id = request.json.get('gitlab_project_id')
    repo = request.json.get('repo', '').strip()
    type_ = request.json.get('type', Component.TYPE_APP)
    dependencies = [ObjectId(c) for c in request.json.get('dependencies', [])]
    _3rd = request.json.get('third_parties', [])
    if not name or not gitlab_project_id:
        raise InvalidUsage('模块名称和Project ID不能为空！')

    try:
        c = await Component.create(name, branch, gitlab_project_id, repo, type_, dependencies, _3rd)
    except DuplicateKeyError:
        raise InvalidUsage('同名模块已存在!')

    return json(jsonify({'id': c.inserted_id}))


@common_bp.put('/api/v1/components')
async def update_component(request):
    _id = request.json.get('_id')
    if not _id:
        raise InvalidUsage('无效的请求参数！')
    name = request.json.get('name', '').strip()
    gitlab_project_id = request.json.get('gitlab_project_id')
    repo = request.json.get('repo', request.json.get('docker_repo', '')).strip()
    type_ = request.json.get('type', Component.TYPE_APP)
    dependencies = [ObjectId(c) for c in request.json.get('dependencies', [])]
    third_parties = request.json.get('third_parties', [])
    if not name or not gitlab_project_id:
        raise InvalidUsage('模块名称和Project ID不能为空！')
    await Component.find_one_and_update(
        {'_id': ObjectId(_id)},
        {'$set': {
            'name': name,
            'gitlab_project_id': gitlab_project_id,
            'repo': repo,
            'type': type_,
            'dependencies': dependencies,
            'third_parties': third_parties,
            'update_time': get_timestamp()}})

    return json({})


@common_bp.get('/api/v1/environments')
async def get_environments(request):
    filter_ = {}
    product = request.args.get('product')
    if product:
        filter_['assign_to.product'] = ObjectId(product)
    q_ = request.args.get('q')
    if q_:
        filter_['$or'] = [
            {'name': {'$regex': '(?i)' + q_}},
            {'ip': {'$regex': q_}},
            {'label': {'$regex': '(?i)' + q_}}]
    if request.args.get('status'):
        filter_['status'] = {'$in': request.args.get('status').split(',')}
    return json(jsonify([e async for e in Environment.find(filter_)]))


@common_bp.post('/api/v1/environments')
async def new_environment(request):
    name = request.json.get('name', '').strip()
    label = request.json.get('label', [])
    ip = request.json.get('ip', '').strip()
    user = request.json.get('user', '').strip() or SSH_USER
    password = request.json.get('password', '').strip() or SSH_PASSWORD
    description = request.json.get('description', '')
    assign_to = request.json.get('assign_to', {})
    settings = request.json.get('settings', {})

    if not name or not ip:
        raise InvalidUsage('name和ip必须设置!')

    try:
        e = await Environment.create(
            name, label, ip, user, password, description, assign_to, settings)
    except DuplicateKeyError:
        raise InvalidUsage('相同名字或IP的环境已存在！')

    return json(jsonify({'id': e.inserted_id}))


@common_bp.put('/api/v1/environments')
async def update_environment(request):
    # NOTE: assign_to only be set on deployment
    _id = request.json.get('_id')
    if not _id:
        raise InvalidUsage('无效的请求参数！')
    force = request.json.get('force', False)
    name = request.json.get('name', '').strip()
    ip = request.json.get('ip', '').strip()
    user = request.json.get('user', '').strip()
    password = request.json.get('password', '').strip()
    filter_ = {'_id': ObjectId(_id)}
    update = {
        'name': name,
        'label': request.json.get('label', []),
        'ip': ip,
        'description': request.json.get('description', ''),
        'user': user,
        'password': password,
        'settings': request.json.get('settings', {}),
        'update_time': get_timestamp()}
    if 'status' in request.json:
        update['status'] = request.json['status']
        if not force:
            filter_['status'] = {'$ne': Environment.BUSY}  # idle <-> maint

    if not name or not ip:
        raise InvalidUsage('name和ip必须设置!')

    await Environment.find_one_and_update(filter_, {'$set': update})

    return json({})


@common_bp.get('/api/v1/environments/reserve')
async def reserve_environment(request):
    assign_type = request.args.get('assign_type', 'ci')
    assign_id = request.args.get('assign_id', request.remote_addr)
    product_id = request.args.get('product_id', 'ci')
    duration = float(request.args.get('duration', 0))
    if duration <= 0:
        raise InvalidUsage('duration should be > 0')

    env = await Environment.find_one_and_update(
        {'$or': [
            {'status': Environment.IDLE},
            {'assign_to.id': assign_id, 'assign_to.type': assign_type}]},
        {'$set': {
            'status': Environment.BUSY,
            'assign_to': {
                'type': assign_type,
                'product': product_id,
                'id': assign_id,
                'expire_in': duration + get_timestamp()},
            'update_time': get_timestamp()}},
        return_document=ReturnDocument.AFTER)

    if not env:
        raise NotFound('no idle environment')

    return json(jsonify({'_id': env['_id'], 'name': env['name'], 'ip': env['ip']}))


@common_bp.delete('/api/v1/environments/free')
async def free_environment(request):
    assign_type = request.args.get('assign_type', 'ci')
    assign_id = request.args.get('assign_id', request.remote_addr)
    env_ip = request.args.get('ip', '')

    await Environment.find_one_and_update(
        {
            'status': Environment.BUSY,
            'ip': env_ip,
            'assign_to.id': assign_id,
            'assign_to.type': assign_type},
        {'$set': {
            'status': Environment.IDLE,
            'assign_to': {},
            'update_time': get_timestamp()}},
        return_document=ReturnDocument.AFTER)

    return json({})


@common_bp.get('/api/v1/features')
async def get_features(request):
    skip = int(request.args.get('skip', 0))
    limit = int(request.args.get('limit', 10))

    filter_ = {}
    product = request.args.get('product')
    if product:
        filter_['product'] = ObjectId(product)
    status = request.args.get('status')
    if status:
        filter_['status'] = {'$in': status.split(',')}

    components = {
        c['_id']: c async for c in Component.find(
            {},
            ['_id', 'name', 'description', 'type', 'repo', 'docker_repo'])}
    features = []
    async for f in Feature.find(filter_, sort=[('update_time', -1)], skip=skip, limit=limit):
        c_ids = f['components']
        f['components'] = []
        for c_id in c_ids:
            component_detail = components[c_id]
            f['components'].append(component_detail)
        features.append(f)

    return json(jsonify({
        'total': await Feature.count_documents(filter_),
        'features': features}))


@common_bp.get('/api/v1/feature/<feature_id>')
async def get_feature_detail(request, feature_id):
    feature = await Feature.find_one({'_id': ObjectId(feature_id)}) or {}
    if not feature:
        return json({})

    product = await Product.find_one({'_id': feature['product']}, ['name', 'components'])
    if product:
        feature['product_name'] = product['name']
    feature['components'] = [c async for c in Component.find(
        {'_id': {'$in': feature['components']}}, ['_id', 'name', 'repo', 'docker_repo'])]
    return json(jsonify(feature))


@common_bp.post('/api/v1/features')
async def new_feature(request):
    name = request.json.get('name', '').strip()
    description = request.json.get('description', '').strip()
    branch = request.json.get('branch', '').strip()
    product = ObjectId(request.json.get('product', ''))
    base_version = request.json.get('base_version')
    components = [ObjectId(c) for c in request.json.get('components', [])]
    if not name or not branch or not product or not components:
        raise InvalidUsage('参数错误!')

    try:
        f = await Feature.create(name, branch, product, base_version, components, [], description)
    except DuplicateKeyError:
        raise InvalidUsage('同名Feature已存在！')

    return json(jsonify({'id': f.inserted_id}))


@common_bp.put('/api/v1/features')
async def update_feature(request):
    _id = request.json.get('_id')
    if not _id:
        raise InvalidUsage('无效的请求参数！')
    name = request.json.get('name', '').strip()
    description = request.json.get('description', '').strip()
    branch = request.json.get('branch', '').strip()
    product = ObjectId(request.json.get('product', ''))
    base_version = request.json.get('base_version')
    components = [ObjectId(c) for c in request.json.get('components', [])]
    if not name or not branch or not product or not components:
        raise InvalidUsage('参数错误!')
    await Feature.find_one_and_update(
        {'_id': ObjectId(_id)},
        {'$set': {
            'name': name,
            'branch': branch,
            'description': description,
            'product': product,
            'base_version': base_version,
            'components': components,
            'update_time': get_timestamp()}})

    return json({})


@common_bp.delete('/api/v1/features')
async def close_feature(request):
    id_ = request.args.get('id')
    if not id_:
        raise InvalidUsage('无效的请求参数！')
    await Feature.find_one_and_update(
        {'_id': ObjectId(id_), 'status': {'$ne': Feature.DONE}},
        {'$set': {
            'status': Feature.CLOSED,
            'update_time': get_timestamp()}})

    return json({})


@common_bp.get('/api/v1/releases')
async def get_releases(request):
    skip = int(request.args.get('skip', 0))
    limit = int(request.args.get('limit', 3))
    filter_ = {}
    product = request.args.get('product')
    if product:
        filter_['product'] = ObjectId(product)
    status = request.args.get('status')
    if status:
        filter_['status'] = {'$in': status.split(',')}
    ref = request.args.get('ref')
    if ref:
        filter_['$or'] = [{'branch': ref}, {'name': ref}]

    if request.args.get('format') == 'simple':  # simple format
        return json(jsonify({
            'total': await Release.count_documents(filter_),
            'releases': [
                rel async for rel in Release.find(
                    filter_, ['name', 'status', 'publish'],
                    sort=[('update_time', -1)],
                    skip=skip,
                    limit=limit)]}))

    products = {p['_id']: p async for p in Product.find({}, ['name', 'components'])}
    features = {f['_id']: f async for f in Feature.find(
        {}, ['name', 'components'])}
    components = {c['_id']: c async for c in Component.find(
        {}, ['name', 'master_name', 'repository', 'repo', 'docker_repo', 'type', 'tags'])}

    def _get_release_product(rel):
        p_id = rel['product']
        return {
            '_id': p_id,
            'name': products[p_id]['name'],
            'components': [components[c_id] for c_id in products[p_id]['components']]
        }

    def _get_release_features(rel):
        return [{
            '_id': f_id,
            'name': features[f_id]['name'],
            'components': [components[c_id] for c_id in features[f_id]['components']]
        } for f_id in rel['features']]

    async def _get_release_merge_requests(rel):
        components = itertools.chain.from_iterable([f['components'] for f in rel['features']])
        return [mr async for mr in MergeRequest.find({
            'component': {'$in': [c['_id'] for c in components]},
            'source_branch': rel['branch'],
            'state': {'$ne': 'closed'}})]

    releases = []
    async for rel in Release.find(filter_, sort=[('update_time', -1)], skip=skip, limit=limit):
        rel['features'] = _get_release_features(rel)
        rel['product'] = _get_release_product(rel)
        rel['merge_requests'] = await _get_release_merge_requests(rel)
        releases.append(rel)

    return json(jsonify({
        'total': await Release.count_documents(filter_),
        'releases': releases}))


@common_bp.get('/api/v1/release/<release_id>')
async def get_release_detail(request, release_id):
    release = await Release.find_one({'_id': ObjectId(release_id)}) or {}
    if not release:
        return json({})

    product = await Product.find_one({'_id': release['product']}, ['name', 'components', 'export_script'])
    if product:
        release['product_name'] = product['name']
        release['product_export_script'] = product.get('export_script', '')
        release['merge_requests'] = [mr async for mr in MergeRequest.find({
            'component': {'$in': product['components']},
            'source_branch': release['branch'],
            'target_branch': 'master'})]

    release['features'] = [
        f async for f in Feature.find(
            {'_id': {'$in': release['features']}},
            ['name', 'status', 'components', 'create_time'])]
    components = {c['_id']: c async for c in Component.find(
        {}, ['name', 'repo', 'docker_repo', 'type'])}
    for feature in release['features']:
        feature['components'] = [
            components[c_id] for c_id in feature['components']]

    return json(jsonify(release))


@common_bp.post('/api/v1/releases')
async def new_release(request):
    #  TODO: new release created, set its features to release state
    name = request.json.get('name', '').strip()
    branch = request.json.get('branch', '').strip()
    product = ObjectId(request.json.get('product', ''))
    base_version = request.json.get('base_version')
    features = [ObjectId(f) for f in request.json.get('features', [])]
    if not name or not branch or not product or not features:
        raise InvalidUsage('参数错误!')

    try:
        release = await Release.create(name, branch, product, base_version, features)
    except DuplicateKeyError:
        raise InvalidUsage('记录已存在！')

    return json({'id': str(release.inserted_id)})


@common_bp.put('/api/v1/releases')
async def update_release(request):
    #  TODO: update its features state
    _id = request.json.get('_id')
    if not _id:
        raise InvalidUsage('无效的请求参数！')
    name = request.json.get('name', '').strip()
    branch = request.json.get('branch', '').strip()
    product = ObjectId(request.json.get('product', ''))
    base_version = request.json.get('base_version')
    features = [ObjectId(f) for f in request.json.get('features', [])]
    if not name or not branch or not product or not features:
        raise InvalidUsage('参数错误!')

    record = await Release.find_one_and_update(
        {'_id': ObjectId(_id)},
        {'$set': {
            'name': name,
            'branch': branch,
            'product': product,
            'base_version': base_version,
            'features': features,
            'update_time': get_timestamp(),
        }})

    if not record:
        raise NotFound('找不到对应的release!')

    return json({})


@common_bp.delete('/api/v1/releases')
async def close_release(request):
    id_ = request.args.get('id')
    if not id_:
        raise InvalidUsage('无效的请求参数！')
    record = await Release.find_one_and_update(
            {'_id': ObjectId(id_), 'status': {'$ne': Release.RELEASED}},
            {'$set': {
                'status': Release.CLOSED,
                'update_time': get_timestamp()}})

    if not record:
        raise NotFound('找不到对应的release!')

    return json({})
