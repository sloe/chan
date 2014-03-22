
import logging
from pprint import pprint, pformat

from sloeconfig import SloeConfig
from sloeerror import SloeError
from sloetreenode import SloeTreeNode

class SloeOrder(SloeTreeNode):
    MANDATORY_ELEMENTS = ("name", "uuid")
    def __init__(self):
        SloeTreeNode.__init__(self, "order", "0a")

    @classmethod
    def new_from_ini_file(cls, ini_filepath, error_info):
        obj = SloeOrder()
        obj.create_from_ini_file(ini_filepath, error_info)
        return obj

    def __repr__(self):
        return "|Order|%s" % pformat(self._d)
