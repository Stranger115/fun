`FUN` is the shortcut of "Test And Automation Online", see its architecture below.

[![pipeline status](https://dev.dingxiang-inc.com:2020/aladdin/tao/badges/master/pipeline.svg)](https://dev.dingxiang-inc.com:2020/aladdin/tao/commits/master)
[![coverage report](https://dev.dingxiang-inc.com:2020/aladdin/tao/badges/master/coverage.svg)](https://dev.dingxiang-inc.com:2020/aladdin/tao/commits/master)

## Architecture

![Overview Arch](arch.png)

TAO acts as the coordinator in the whole continues delivery cycle. It targets the following features:

- [x] manage products
- [x] manage components
- [x] create new release and show its cci, code review and pci status
- [x] publish release
- [x] create new feature and show its cci status
- [x] manage test environments
- [x] deploy release or feature to test environment
- [x] gitlab authentication
- [ ] user role system including viewer, developer and administrator
- [ ] show release issues from [TAPD](https://tapd.cn)
- [ ] publish release to online environment
- [ ] mobile device support

`TAO` is based on [sanic](https://sanic.readthedocs.io/en/latest/) with [asyncio](https://docs.python.org/3/library/asyncio.html) support and [MongoDB](https://www.mongodb.com/), it contains three components:

* web - including web api and web ui
    * api - RESTful API used by web ui and ci
    * ui - used by end user, based on antd and reactjs
* clerk - background task queue and cron job
* tools - useful command line tools like deploy

![Internal Arch](internal.png)

## Development

### Pre-requirements

* Python 3.6+ (docker running on Python 3.7)
* Linux (Windows/Mac should be able to work)
* pip3
* nodejs 8.*

### Fetch the code and dependencies

```sh
git clone https://dev.dingxiang-inc.com:2020/aladdin/tao.git

cd tao
sudo pip3 install -r requirements.txt -i https://pypi.douban.com/simple
sudo pip3 install pytest -i https://pypi.douban.com/simple  # for unit test

# UI dev
cd src/tao/web/www
npm install  # install UI dependencies
```

### Unit Test

`TAO` use [pytest](https://pytest.org) as unit test framework, to execute unit test, run the command below:

```sh
cd tao  # change to root path of TAO
export PYTHONPATH=$PWD/src  # set PYTHONPATH=%CD%/src
pytest -s ./tst
```

### Run and debug

1. tao.web API service
```sh
export PYTHONPATH=$PWD/src
python3 -m tao.web
nohup python3 -m tao.web &
python3 -m tao.web
python -m tao.web
```

1. tao.web UI dev server
```sh
cd src/tao/web/www
npm start
```

1. tao.web clerk service
```sh
export PYTHONPATH=$PWD/src
python3 -m tao.clerk
```

1. Open [http://127.0.0.1:3000](http://127.0.0.1:3000) to visit local hosted `TAO` UI
