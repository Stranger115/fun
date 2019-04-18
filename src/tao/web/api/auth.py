import logging
from sanic import Blueprint
from sanic.request import Request
from sanic.response import HTTPResponse, redirect, json
from sanic.exceptions import Unauthorized
from urllib.parse import urlencode
from tao.settings import GITLAB_AUTHORIZE_URL, GITLAB_TOKEN_URL, GITLAB_API_URL, GITLAB_OAUTH_APP_ID, GITLAB_OAUTH_APP_SECRET, GITLAB_OAUTH_REDIRECT_URI


auth_bp = Blueprint('auth')


@auth_bp.get('/api/v1/auth')
async def user_auth(request: Request) -> HTTPResponse:
    if 'code' not in request.args:  # got code, try to fetch token
        logging.debug('try to fetch code from gitlab')
        return redirect(GITLAB_AUTHORIZE_URL + '?' + urlencode({
            'client_id': GITLAB_OAUTH_APP_ID,
            'response_type': 'code',
            'scope': 'read_user',
            'redirect_uri': GITLAB_OAUTH_REDIRECT_URI
        }, quote_via=lambda e, *args: e))

    logging.debug('got code, try to fetch access_token')
    async with request.app.async_session.post(GITLAB_TOKEN_URL, data={
        'grant_type': 'authorization_code',
        'client_id': GITLAB_OAUTH_APP_ID,
        'client_secret': GITLAB_OAUTH_APP_SECRET,
        'code': request.args['code'],
        'redirect_uri': GITLAB_OAUTH_REDIRECT_URI
    }) as resp:
        token_info = await resp.json()
        if 'access_token' not in token_info:
            logging.debug('no access_token read, but got "%s"' % token_info)
            raise Unauthorized('token not fetched')

    async with request.app.async_session.get(GITLAB_API_URL + '/user?access_token=' + token_info['access_token']) as resp:
        user_info = await resp.json()
        if 'username' not in user_info:
            raise Unauthorized('userinfo not fetched, but got "%s"' % user_info)
        request['session']['user'] = user_info
        logging.debug('got user info "%s"' % user_info)

    return redirect('/')


@auth_bp.get('/api/v1/logout')
async def logout(request):
    if request['session'].pop('user', None) is None:
        logging.error('user try to logout but not login')
    return json({})


@auth_bp.get('/api/v1/user')
async def get_user_info(request):  # user should be there, otherwise user_auth middleware will reject
    if request.ip == '127.0.0.1':
        return json({'name': 'dev', 'username': 'localdev'})
    return json(request['session']['user'])
