
import os
from pprint import pprint, pformat

from sloeconfig import SloeConfig
from sloeerror import SloeError
from sloetreenode import SloeTreeNode


class SloeConfigSpec(SloeTreeNode):
    MANDATORY_ELEMENTS = {
        "loglevel": "Log level - one of DEBUG, INFO, WARNING or ERROR",
        "primacies": "Primacies to consider - usually primary,final",
        "sandboxdir": "Path to sandbox directory",
        "treeroot": "Path to root of data directory",
        "worths": "Worths to consider - usually precious,derived,junk"
    }
    MANDATORY_ELEMENTS.update(SloeTreeNode.MANDATORY_ELEMENTS)
    OPTIONAL_ELEMENTS = {
        "aeprojectdir": "(Relative) path to After Effect project directory",
        "ffprobe": "(Relative) path to ffprobe command",
        "plugindirs": "(Relative) paths to plugin directories"
    }
    OPTIONAL_ELEMENTS.update(SloeTreeNode.OPTIONAL_ELEMENTS)


    def __init__(self):
        SloeTreeNode.__init__(self, "config", "0c")


    @classmethod
    def new_from_ini_file(cls, ini_filepath, error_info):
        obj = SloeConfigSpec()
        obj.create_from_ini_file(ini_filepath, error_info, add_to_library=False)
        return obj


    def verify_confirm_missing(self, element):
        return element != "uuid"


    def add_filepath_info(self, filepath):
        self._d["_location"] = os.path.dirname(filepath)


    def apply_to_config(self, config, section):
        for k, v in self._d.iteritems():
            if not k.startswith("_"):
                config.set_value(section, k, v)


    def __repr__(self):
        return "|SloeConfigSpec|%s" % pformat(self._d)


SloeTreeNode.add_factory("SLOECONFIGSPEC", SloeConfigSpec)
