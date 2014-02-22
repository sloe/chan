
import imp
import logging
import os
from pprint import pformat, pprint
import re
import sys
import traceback

from sloeconfig import SloeConfig
from sloeerror import SloeError

sloe_register_plugin = True

class SloePlugInManager(object):
    instance = None
    def __init__(self):
        self.plugins = {}
        
        
    @classmethod
    def inst(cls):
        if cls.instance is None:
            cls.instance = SloePlugInManager()
        return cls.instance        

    
    def load_plugins(self):
        glb_cfg = SloeConfig.inst()
        root = SloeConfig.get_option("script_dir")
        plugin_dirs = glb_cfg.get_value("global", "plugindirs")
        for plugin_dir in plugin_dirs.split(os.path.pathsep):
            dir_path = os.path.join(root, plugin_dir)
            
            if not os.path.isdir(dir_path):
                logging.warn("Cannot open configured plugin directory %s" % dir_path)
            else:
                for root, dirs, filenames in os.walk(dir_path):
                    for filename in filenames:
                        match =  re.match(r'(sloeplugin_)([^/]+)\.py$', filename)
                        if match:
                            name = "".join(match.group(1, 2))
                            short_name = match.group(2)
                            file_obj = None
                            try:
                                try:
                                    # Import using variable as module name
                                    (file_obj, import_path, description) = imp.find_module(name, [root])
                                    imp.load_module(name, file_obj, import_path, description)
                                    logging.info("Loaded plugin '%s'" % short_name)
                                except Exception, e:
                                    try:
                                        logging.error("".join(traceback.format_tb(sys.exc_info()[2])))
                                    except:
                                        pass
                                    logging.error("Plugin '%s' failed to load: %s" % (name, str(e)))

                            finally:
                                if file_obj is not None:
                                    file_obj.close()
            
            
    def register_plugin(self, name, spec):
        logging.info("Registering plugin '%s'" % name)
        
        if name in self.plugins:
            raise SloeError("Duplicate plugin name '%s'" % name)
            
        if "methods" not in spec:
            raise SloeError("Plugin '%s' does not define methods" % name)
                    
        self.plugins[name] = spec
        
        
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
        return method(obj, *args, **keywords)
    