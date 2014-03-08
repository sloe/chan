
from pprint import pformat

from sloeconfig import SloeConfig
from sloeerror import SloeError
from sloetreenode import SloeTreeNode

class SloeTransferJob(SloeTreeNode):
    MANDATORY_ELEMENTS = ("name", "priority", "transfer_type", "uuid")
    def __init__(self):
        SloeTreeNode.__init__(self, "transferjob", "07")


    def __repr__(self):
        return "|TransferJob|%s" % pformat(self._d)
