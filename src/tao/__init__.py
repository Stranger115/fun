import asyncio
try:
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    import sys
    sys.stderr.write('uvloop module not found!')

try:
    from tao.version import __version__
except ImportError:
    __version__ = 'master'
