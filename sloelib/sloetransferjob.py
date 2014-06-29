
from pprint import pformat

from sloeconfig import SloeConfig
from sloeerror import SloeError
from sloetreenode import SloeTreeNode

class SloeTransferJob(SloeTreeNode):
    MANDATORY_ELEMENTS = {
        "name": "Primary name of the item",
        "priority": "Priority of the item",
        "transfer_type": "Type of transfer used for items"
    }
    MANDATORY_ELEMENTS.update(SloeTreeNode.MANDATORY_ELEMENTS)
    OPTIONAL_ELEMENTS = {
    }
    OPTIONAL_ELEMENTS.update(SloeTreeNode.OPTIONAL_ELEMENTS)


    def __init__(self):
        SloeTreeNode.__init__(self, "transferjob", "07")


    def __repr__(self):
        return "|TransferJob|%s" % pformat(self._d)
