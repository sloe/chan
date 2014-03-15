
import imp
import logging
import os
from pprint import pformat, pprint
import re
import sys
import traceback

from sloeconfig import SloeConfig
from sloeerror import SloeError

class SloePlugInManager(object):
    instance = None
    def __init__(self):
        self.plugins = {}
        self.commands = {}
        self.varsubsts = {}
        
        
    @classmethod
    def inst(cls):
        if cls.instance is None:
            cls.instance = SloePlugInManager()
        return cls.instance
            
            
    def register_plugin(self, name, spec):
        logging.info("Registering plugin '%s'" % name)
        
        if name in self.plugins:
            raise SloeError("Duplicate plugin name '%s'" % name)
            
        if "methods" not in spec:
            raise SloeError("Plugin '%s' does not define methods" % name)
                    
        self.plugins[name] = spec
        
        for method in spec["methods"].keys():
            if method.startswith("command_"):
                self.commands[method[8:]] = {
                "plugin" : name,
                "method" : method}
            elif method.startswith("varsubst_"):
                self.varsubsts[method[9:]] = {
                "plugin" : name,
                "method" : method}
            
        
        
    def call_plugin(self, name, method_name, *args, **keywords):
        plugin = self.plugins.get(name, None)
        if plugin is None:
            raise SloeError("Plugin name '%s' does not exist or failed to load" % name)
        methods = plugin.get("methods", None)
        method = methods.get(method_name, None)
        if not method:
            raise SloeError("No method '%s' in PlugIn '%s'" % (method_name, name))
        
        obj = plugin.get("object", None)
        if obj is None:
            raise SloeError("Plugin name '%s' - no object defined" % name)        
        return method(*args, **keywords)
    