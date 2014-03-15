
import logging
import os
import sys
import types
from pprint import pprint, pformat

from sloeconfig import SloeConfig
from sloeerror import SloeError
from sloepluginmanager import SloePlugInManager

class SloeBasePlugIn(object):
    def __init__(self, name):
        self.name = name
        methods = {}
        for k in dir(self):
            if not k.startswith("_"):
                attr = getattr(self, k)
                if isinstance(attr, types.MethodType):
                    methods[k] = attr
                
        spec = {
            "methods": methods,
            "object": self
        }
        SloePlugInManager.inst().register_plugin(name, spec)    
    