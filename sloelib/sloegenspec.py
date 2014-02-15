
import logging
from pprint import pprint, pformat
import re
import uuid

from sloeconfig import SloeConfig
from sloeerror import SloeError
from sloetreenode import SloeTreeNode

class SloeGenSpec(SloeTreeNode):
    MANDATORY_ELEMENTS = ("name", "uuid")
    def __init__(self):
        SloeTreeNode.__init__(self, "genspec")

    @classmethod
    def new_from_ini_file(cls, ini_filepath, error_info):
        genspec = SloeGenSpec()
        genspec.create_from_ini_file(ini_filepath, error_info)
        return genspec


    def __repr__(self):
        return "|GenSpec|%s" % pformat(self._d)