
from sloeconfig import SloeConfig
from sloeerror import SloeError
from sloetreenode import SloeTreeNode

class SloeRenderJob(SloeTreeNode):
    MANDATORY_ELEMENTS = ("name", "priority", "uuid")
    def __init__(self):
        SloeTreeNode.__init__(self, "renderjob", "05")


    def __repr__(self):
        return "|RenderJob|%s" % pformat(self._d)
