class MockRequest(object):
    def __init__(self, **args):
        self.args = args
        self.remote_addr = '127.0.0.1'
        self.ip = '127.0.0.1'
        self.path = '/'
        self.session = {}

    def __getitem__(self, k):
        return getattr(self, k)
