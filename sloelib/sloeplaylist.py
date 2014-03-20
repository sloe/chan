
import logging
from pprint import pprint, pformat

from sloeconfig import SloeConfig
from sloeerror import SloeError
from sloetreenode import SloeTreeNode

class SloePlaylist(SloeTreeNode):
    MANDATORY_ELEMENTS = ("name", "priority", "uuid")
    def __init__(self):
        SloeTreeNode.__init__(self, "playlist", "09")

    @classmethod
    def new_from_ini_file(cls, ini_filepath, error_info):
        obj = SloePlaylist()
        obj.create_from_ini_file(ini_filepath, error_info)
        obj.priority = float(obj.priority)
        return obj

    def __repr__(self):
        return "|SloePlaylist|%s" % pformat(self._d)
