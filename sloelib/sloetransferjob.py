
from pprint import pformat

from sloeconfig import SloeConfig
from sloeerror import SloeError
from sloetreenode import SloeTreeNode

class SloeTransferJob(SloeTreeNode):
    MANDATORY_ELEMENTS = {
        "common_id": "IDs of related items in common ID format",
        "leafname": "Leafname (filename) of the item",
        "name": "Primary name of the item",
        "payload_type": "Type of object being transferred (item, playlist, etc.)",
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
