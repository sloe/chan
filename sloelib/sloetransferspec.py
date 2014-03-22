
import logging
from pprint import pprint, pformat

from sloeconfig import SloeConfig
from sloeerror import SloeError
from sloetreenode import SloeTreeNode

class SloeTransferSpec(SloeTreeNode):
    MANDATORY_ELEMENTS = ("name", "priority", "transfer_type", "uuid")
    def __init__(self):
        SloeTreeNode.__init__(self, "transferspec", "06")

    @classmethod
    def new_from_ini_file(cls, ini_filepath, error_info):
        obj = SloeTransferSpec()
        obj.create_from_ini_file(ini_filepath, error_info)
        obj.priority = float(obj.priority)
        return obj

    def __repr__(self):
        return "|TransferSpec|%s" % pformat(self._d)


SloeTreeNode.add_factory("TRANSFERSPEC", SloeTransferSpec)