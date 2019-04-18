import os
import aiohttp

DB_CONN = 'mongodb://127.0.0.1:27017/fun'

SSH_USER = 'root'
SSH_PASSWORD = '1997zxcV'

GITLAB_URL = 'https://dev.dingxiang-inc.com'
GITLAB_HOST = '10.0.0.202'
GITLAB_API_URL = GITLAB_URL + '/api/v4'
GITLAB_WEBHOOK_TOKEN = '76bf59fc4f95'
GITLAB_API_TOKEN = 'vLWLzxaJfhthDEuL232m'
GITLAB_READ_TOKEN = 'AEqyV6xPKHEzes63BW7i'

# gitlab auth
GITLAB_AUTHORIZE_URL = GITLAB_URL + '/oauth/authorize'
GITLAB_TOKEN_URL = GITLAB_URL + '/oauth/token'
GITLAB_OAUTH_APP_ID = '405c2019377e86e265082cbf0c1448911d9db98fa134fbf04afd66928e74b152'
GITLAB_OAUTH_APP_SECRET = '26ae0116eecec872a2d0988d36aebf794eac72677c59673781289d4d3768b3e5'
GITLAB_OAUTH_REDIRECT_URI = 'http://tao.dx-corp.top:19898/api/v1/auth'
API_WHITELIST = [
    '/api/v1/status',
    '/api/v1/auth',
    '/api/v1/cci/script',
    '/api/v1/cci/lock',
    '/api/v1/cci/trigger',
    '/api/v1/pci/trigger',
    '/api/v1/monitor/hosts',
    '/api/v1/monitor/aggrs',
    '/api/v1/monitor/nodata',
    '/api/v1/monitor/plugins',
    '/api/v1/monitor/strategies',
    '/api/v1/gitlab/webhook',
    '/api/v1/gitlab/artifacts',
    '/favicon.ico',
    '/manifest.json',
]  # will ignore user auth

# dingding related settings
DINGDING_TOKRN_API = 'https://oapi.dingtalk.com/gettoken'
DINGDING_AGENT_API = 'https://oapi.dingtalk.com/message/send'
DINGDING_ROBOT_API = 'https://oapi.dingtalk.com/robot/send'
DINGDING_PARTY_URL = 'https://oapi.dingtalk.com/department/list'
DINGDING_USER_URL = 'https://oapi.dingtalk.com/user/list'

DINGDING_AGENT_ID = 220849157
DINGDING_CORP_ID = 'dingaja42an7krypim9g'
DINGDING_CORP_SECRET = 'DsVXkbuH9p4vseWxoZNQi9m153HYfkMpVfI63Ccyq1YKNWgQfYQ7ujvNNTxCf1lP'
DINGDING_TIME = 2
DINGDING_SEND_TYPE_TIME = 24
DINGDING_ADMINS = ['0410375944789941']

# the group - robot token mapping is rarely changed, use const settings here
DINGDING_GROUP_ROBOT_TOKENS = {
    69346464: {
        'access_token': '32db35262b0763ac7c4dd9ed9ef162e97462b71b316b5061f9278ab143a7418d',
        'name': '乾象平台研发'},
    69238517: {
        'access_token': '0e27df7565b1861d943f2ff711d5e2690ec6d985e51ab790d03fc8a39eefb686',
        'name': '前端UED'},
    69319456: {
        'access_token': 'b831b436cd5d1f19a4184879fdf16b4b78a6a4c574a3c8cf96a5150b5a757601',
        'name': '风控二部'},
    69382500: {
        'access_token': '25b4b6bba952fb5b5bc915d1acfe3ff38278c2d903ffe1530d2af8ee1f6a7817',
        'name': '风控一部'},
}

PROXY_AUTH = aiohttp.BasicAuth('dingding', 'fgQlg67C')
PROXY_ADDR = 'http://118.25.100.104:8888'


# code review rule
MIN_UPVOTES = 1  # upvotes >= MIN_UPVOTES
MAX_DOWNVOTES = 0  # downvotes <= MAX_DOWNVOTES


#
PRODUCTS_LINE_LIMIT = 4
