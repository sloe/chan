
import logging
from pprint import pprint, pformat
import re
import uuid

from sloeconfig import SloeConfig
from sloeerror import SloeError
from sloetreenode import SloeTreeNode

class SloeGenSpec(SloeTreeNode):
    MANDATORY_ELEMENTS = {
        "name": "Primary name of the item",
        "priority": "Priority of the item"
    }
    MANDATORY_ELEMENTS.update(SloeTreeNode.MANDATORY_ELEMENTS)
    OPTIONAL_ELEMENTS = {
        "gen_type": "Name of generator to use",
        "input_conformed_frame_rate": "Frame rate used for input footage by the generator (frames per second)",
        "output_description": "Description of output",
        "output_extension": "Filename extension of output file",
        "output_frame_rate": "Frame rate of output file (frames per second)",
        "output_frames_per_input_frame": "Output frames generated per input frame",
        "output_note": "Notes about output",
        "output_short_description": "Short description of output",
        "output_suffix": "Suffix added to output filename",
        "speed_factor": "Viewable speed factor - output speed/input speed"
    }
    OPTIONAL_ELEMENTS.update(SloeTreeNode.OPTIONAL_ELEMENTS)


    def __init__(self):
        SloeTreeNode.__init__(self, "genspec", "03")


    @classmethod
    def new_from_ini_file(cls, ini_filepath, error_info):
        obj = SloeGenSpec()
        obj.create_from_ini_file(ini_filepath, error_info)
        obj.priority = float(obj.priority)
        return obj


    def __repr__(self):
        return "|GenSpec|%s" % pformat(self._d)


SloeTreeNode.add_factory("GENSPEC", SloeGenSpec)
