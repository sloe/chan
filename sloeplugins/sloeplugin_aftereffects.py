
import logging
import os
from pprint import pformat, pprint
import sloelib

class SloePluginAfterEffects(object):
    instance = None
    def __init__(self):
        self.aerender = self.derive_aerender_path()
        
        
    def derive_aerender_path(self):
        for path in self.path_list():
            if os.path.isfile(path):
                logging.info("Selected aerender binary %s" % path)
                return path

        logging.warn("Unable to find After Effects binary aerender.exe.")
        return None
    
    
    def path_list(self):
        glb_cfg = sloelib.SloeConfig.get_global()
        aerender_path = glb_cfg.get_or_none("global", "aerender")
        config_paths = []
        if aerender_path:
            config_paths.append(aerender_path)
            
        return config_paths + [
            "C:\\Program Files\\Adobe\\Adobe After Effects CS7\\Support Files\\aerender.exe",
            "C:\\Program Files\\Adobe\\Adobe After Effects CS6.5\\Support Files\\aerender.exe",
            "C:\\Program Files\\Adobe\\Adobe After Effects CS6\\Support Files\\aerender.exe",
            "C:\\Program Files\\Adobe\\Adobe After Effects CS5.5\\Support Files\\aerender.exe",
            "C:\\Program Files\\Adobe\\Adobe After Effects CS5\\Support Files\\aerender.exe"
        ]

    
    def do_render_job(self, genspec, item, outputspec):
        logging.info("Performing render job for '%s'" % item.name)
        if self.aerender is None:
            raise sloelib.SloeError("Unable to render - cannt find aerender.exe") 
            
        sandbox = sloelib.SloeSandbox("aftereffects")
        sandbox.create(files_to_copy = {

        })
        
        command = [
            self.aerender,
            "-project", "ae_project_path",
            "-comp", "Output Comp",
            "-e", str("dest_frames"),
            "-OMtemplate", "output_module",
            "-reuse",
            "-output", "sandbox_output_pathname"            
        ]
        print "genspec=%s" % pformat(genspec)
        print "item=%s" % pformat(item)
        print "outputspec=%s" % pformat(outputspec)
        sandbox.destroy()
    
    
    @classmethod
    def register(cls):
        obj = SloePluginAfterEffects()
        spec = {
            "methods": {
                "do_render_job" : cls.do_render_job
            },
            "object": obj
        }
        sloelib.SloePlugInManager.inst().register_plugin("aftereffects", spec)
        

SloePluginAfterEffects.register()

    