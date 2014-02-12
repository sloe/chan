
import logging
from pprint import pprint, pformat
import re
import uuid

from sloeconfig import SloeConfig
from sloeerror import SloeError
from sloetreenode import SloeTreeNode

class SloeOutputSpec(SloeTreeNode):
  MANDATORY_ELEMENTS = ("name", "uuid")
  def __init__(self):
    SloeTreeNode.__init__(self, "outputspec")

  @classmethod
  def new_from_ini_file(cls, ini_filepath, error_info):
    outputspec = SloeOutputSpec()
    outputspec.create_from_ini_file(ini_filepath, error_info)
    return outputspec

  def __repr__(self):
    return pformat(self._d)