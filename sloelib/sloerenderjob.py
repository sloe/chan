
from pprint import pformat

from sloeconfig import SloeConfig
from sloeerror import SloeError
from sloetreenode import SloeTreeNode

class SloeRenderJob(SloeTreeNode):
    MANDATORY_ELEMENTS = {
        "common_id": "IDs of related items in common ID format",
        "leafname": "Leafname (filename) of the item",
        "name": "Primary name of the item",
        "priority": "Priority of the item"
    }
    MANDATORY_ELEMENTS.update(SloeTreeNode.MANDATORY_ELEMENTS)
    OPTIONAL_ELEMENTS = {
    }
    OPTIONAL_ELEMENTS.update(SloeTreeNode.OPTIONAL_ELEMENTS)


    def __init__(self):
        SloeTreeNode.__init__(self, "renderjob", "05")


    def __repr__(self):
        return "|RenderJob|%s" % pformat(self._d)
