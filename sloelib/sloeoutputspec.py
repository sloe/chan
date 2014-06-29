
import logging
from pprint import pprint, pformat
import re
import uuid

from sloeconfig import SloeConfig
from sloeerror import SloeError
from sloetreenode import SloeTreeNode

class SloeOutputSpec(SloeTreeNode):
    MANDATORY_ELEMENTS = {
        "name": "Primary name of the item",
        "output_path": "Path expression used to generate destination directory of output",
        "priority": "Priority of the item"
    }
    MANDATORY_ELEMENTS.update(SloeTreeNode.MANDATORY_ELEMENTS)
    OPTIONAL_ELEMENTS = {
        "genspec_name": "Name of GenSpec used to generate output",
        "glob_include": "Glob expression used to select input items"
    }
    OPTIONAL_ELEMENTS.update(SloeTreeNode.OPTIONAL_ELEMENTS)


    def __init__(self):
        SloeTreeNode.__init__(self, "outputspec", "04")


    @classmethod
    def new_from_ini_file(cls, ini_filepath, error_info):
        outputspec = SloeOutputSpec()
        outputspec.create_from_ini_file(ini_filepath, error_info)
        outputspec.priority = float(outputspec.priority)
        return outputspec


    def __repr__(self):
        return "|OutputSpec|%s" % pformat(self._d)


SloeTreeNode.add_factory("OUTPUTSPEC", SloeOutputSpec)