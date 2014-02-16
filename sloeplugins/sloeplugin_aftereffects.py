
import logging
import os
from pprint import pformat, pprint
import subprocess
import sys

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
        glb_cfg = sloelib.SloeConfig.get_global()        
        logging.info("Performing render job for '%s'" % item.name)
        if self.aerender is None:
            raise sloelib.SloeError("Unable to render - cannot find aerender.exe") 
            
        sandbox = sloelib.SloeSandbox("aftereffects")
        src_movie = item.get_file_path()
        dest_movie = "source_footage%s" % os.path.splitext(src_movie)[1]
        output_movie = "source_footage%s" % os.path.splitext(src_movie)[1]
        
        ae_proj_subdir = glb_cfg.get("global", "aeprojectdir")
        script_dir = glb_cfg.get_option("script_dir")
        src_project = os.path.join(script_dir, ae_proj_subdir, genspec.aftereffects_project)
        dest_project = os.path.basename(src_project)
        
        sandbox.create(files_to_copy = {
            src_project : dest_project,
            src_movie : dest_movie
        })
        
        if glb_cfg.get_option("prerenderabort"):
            logging.info("Aborting due to --prerenderabort flag")
            sys.exit(1)
        command = [
            self.aerender,
            "-project", sandbox.get_sandbox_path_for_source(src_project),
            "-comp", "Output Comp",
            "-e", str("60"),
            "-OMtemplate", genspec.aftereffects_outputmodule,
            "-reuse",
            "-output", sandbox.get_sandbox_path(genspec.aftereffects_outputfilename)           
        ]
        

        print "genspec=%s" % pformat(genspec)
        print "item=%s" % pformat(item)
        print "outputspec=%s" % pformat(outputspec)
        
        logging.info("Executing command %s" % " ".join(command))
        
        p = subprocess.Popen(command, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        (stdout, stderr) = p.communicate()
        if p.returncode != 0:        
            raise sloelib.SloeError("Command failed with return code %d: %s\n%s" % (p.returncode, "".join(stderr), "".join(stdout)))        
        
        if glb_cfg.get_option("postrenderabort"):
            logging.info("Aborting due to --postrenderabort flag")
            sys.exit(1) 
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

    