''' models that is used by clerk and web
model relation map:


                                                                     PciBuild * N
                                                                      /
   component-A --\                                                   /
                  \                                                 /      component-A
                   \                                               /        /
   component-B - feature-A                                     release-1 --+
              \      \                                           /          \
               \      +-------------- product ------------------+          component-B
                \    /               /       \                   \
 component-C --- feature-B          /         \                release-2
                             component-A   component-B
                                 /              \
                                /                \
                          Pipeline * N       Pipeline * N
'''
from .base import BaseModel
from .product import Product, Order
from .user import AllUser
from .message import Message
from .task import Task
from .event import GitlabEvent
from .dns import Dns
from .component import Component
from .feature import Feature
from .release import Release
from .gitlab import Pipeline, MergeRequest
from .cci import CciBuild
from .pci import PciBuild
from .env import Environment
from .inform import PipelineStatus, DingDingUser


def init_db(loop):
    ''' initialize the DB connection, it should be called at the server start '''
    BaseModel.init(loop)
