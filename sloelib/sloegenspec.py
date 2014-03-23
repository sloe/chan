
import logging
from pprint import pprint, pformat
import re
import uuid

from sloeconfig import SloeConfig
from sloeerror import SloeError
from sloetreenode import SloeTreeNode

class SloeGenSpec(SloeTreeNode):
    MANDATORY_ELEMENTS = ("name", "priority", "uuid")
    def __init__(self):
        SloeTreeNode.__init__(self, "genspec", "03")

    @classmethod
    def new_from_ini_file(cls, ini_filepath, error_info):
        obj = SloeGenSpec()
        obj.create_from_ini_file(ini_filepath, error_info)
        obj.priority = float(obj.priority)
        return obj


    def __repr__(self):
        return "|GenSpec|%s" % pformat(self._d)
    
    
SloeTreeNode.add_factory("GENSPEC", SloeGenSpec)
