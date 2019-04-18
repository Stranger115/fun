import pytest
from sanic.exceptions import Unauthorized
from tao.web.api import auth
from test_common import MockRequest
from tao.utils import read_async_result


def test_user_auth(monkeypatch):
    def _mock_redirect(url):
        return url

    class _MockApp(object):
        pass

    class _MockSession(object):
        def __init__(self, mock_response):
            self._response = iter(mock_response)

        def post(self, url, data, **kwargs):
            return _MockResponse(next(self._response))

        def get(self, url):
            return _MockResponse(next(self._response))

        def __setitem__(self, k, v):
            setattr(self, k, v)

    class _MockResponse(object):
        def __init__(self, data):
            self.data = data

        async def __aenter__(self):
            return self

        async def json(self):
            return self.data

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass

    monkeypatch.setattr(auth, 'redirect', _mock_redirect)
    assert read_async_result(auth.user_auth(MockRequest())) == 'https://dev.dingxiang-inc.com/oauth/authorize?client_id=405c2019377e86e265082cbf0c1448911d9db98fa134fbf04afd66928e74b152&response_type=code&scope=read_user&redirect_uri=http://tao.dx-corp.top:19898/api/v1/auth'

    request = MockRequest(code=['6eb8b155152bde9223408f359f7e1868d77da0275cda2ba46dbfd356919d519d'])
    request.session = {}
    request.app = _MockApp()
    request.app.async_session = _MockSession([
        {'message': 401},
    ])
    with pytest.raises(Unauthorized):
        read_async_result(auth.user_auth(request))

    request.app.async_session = _MockSession([
        {'access_token': 'cf93aa9e6a8a79a703e802661cb328f8a07056d284d2cc2eb9499478dd0d8b86', 'token_type': 'bearer', 'refresh_token': '1d6be37a9f953aa533723e871b3d25678de46f55fc5d6cdbd753743fed5ebf98', 'scope': 'read_user', 'created_at': 1551670350},
        {'id': 105, 'name': '张裕', 'username': 'zhangyu', 'state': 'active', 'avatar_url': None, 'web_url': 'https://dev.dingxiang-inc.com:2020/zhangyu', 'created_at': '2018-07-03T12:33:10.423+08:00', 'bio': '', 'location': '', 'public_email': '', 'skype': '', 'linkedin': '', 'twitter': '', 'website_url': '', 'organization': '', 'last_sign_in_at': '2019-02-22T11:49:27.052+08:00', 'confirmed_at': '2018-07-03T12:33:10.124+08:00', 'last_activity_on': '2019-03-04', 'email': 'zhangyu@dingxiang-inc.com', 'theme_id': 1, 'color_scheme_id': 1, 'projects_limit': 100, 'current_sign_in_at': '2019-03-04T11:08:32.443+08:00', 'identities': [{'provider': 'ldapmain', 'extern_uid': 'uid=zhangyu,ou=users,dc=dingxiang-inc,dc=com'}], 'can_create_group': True, 'can_create_project': True, 'two_factor_enabled': False, 'external': False, 'private_profile': None}
    ])
    assert read_async_result(auth.user_auth(request)) == '/'
    assert request['session']['user']['username'] == 'zhangyu'
