
import logging
import math
import os
from pprint import pformat, pprint
import shutil
import subprocess
import sys

import sloelib


class SloePluginAfterEffects(object):
    def __init__(self):
        self.aerender = None
    
    
    def derive_aerender_path(self):
        for path in self.path_list():
            if os.path.isfile(path):
                logging.info("Selected aerender binary %s" % path)
                return path

        logging.warn("Unable to find After Effects binary aerender.exe.")
        return None
    
    
    def path_list(self):
        glb_cfg = sloelib.SloeConfig.inst()
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
        
        final_output_path = sloelib.SloeOutputUtil.get_output_path(genspec, item, outputspec)
        if not os.path.isdir(os.path.dirname(final_output_path)):
            os.makedirs(os.path.dirname(final_output_path))
            
        lock_path = final_output_path + '.lock'
        if os.path.isfile(lock_path):
            raise sloelib.SloeError("Abandoning render because lock file '%s' exists" % lock_path)
        
        with open(lock_path, mode="w") as f:
             f.write("%d\n%s (PID=%d) has locked this output destination" % (os.getpid(), __file__, os.getpid()))
        
        try:
            self.do_render_to_path(genspec, item, outputspec, final_output_path)
        
        finally:
            os.unlink(lock_path)
            
            
        
    def do_render_to_path(self, genspec, item, outputspec, final_output_path):
        logging.info("Performing render job for '%s'" % item.name)
        if self.aerender is None:
            self.aerender = self.derive_aerender_path()
        if self.aerender is None:
            raise sloelib.SloeError("Unable to render - cannot find aerender.exe") 
            
        sandbox = sloelib.SloeSandbox("aftereffects")
        src_movie = item.get_file_path()
        dest_movie = "source_footage%s" % os.path.splitext(src_movie)[1]
        output_movie = "source_footage%s" % os.path.splitext(src_movie)[1]
        
        ae_proj_subdir =  sloelib.SloeConfig.get_global("aeprojectdir")
        script_dir = sloelib.SloeConfig.get_option("script_dir")
        src_project = os.path.join(script_dir, ae_proj_subdir, genspec.aftereffects_project)
        dest_project = os.path.basename(src_project)
        
        sandbox.create(files_to_copy = {
            src_project : dest_project,
            src_movie : dest_movie
        })
        
        if sloelib.SloeConfig.get_option("prerenderabort"):
            logging.info("Aborting due to --prerenderabort flag")
            sys.exit(1)
         
        conformed_frame_rate = sloelib.SloeUtil.get_canonical_frame_rate(item.video_avg_frame_rate)
        
        output_to_input_frame_factor = (float(genspec.output_frame_rate) /
            (float(conformed_frame_rate) * sloelib.SloeUtil.fraction_to_float(genspec.speed_factor)))
        # Use math.trunc to round down, so when speeding up (speed_factor > 1) we don't generate
        # frames after the input source has run out
        last_frame = math.trunc(float(item.video_nb_frames) * output_to_input_frame_factor)
            
        # After Effects numbers frames from zero, so the last frame is one less than the number of frames

        if output_to_input_frame_factor < 1:
            last_frame -= 1
        else:
            # When slowing down, Twitor will 'reach out' to the next frame to blend it, which, as the
            # frame beyond the last inout frame is blank, darkens the image.  This correction stops
            # the render just before that happens
            last_frame -= output_to_input_frame_factor

        if last_frame < 1:
            last_frame = 1
            
        sandbox_output_path = sandbox.get_sandbox_path(genspec.aftereffects_outputfilename)
            
        command = [
            self.aerender,
            "-project", sandbox.get_sandbox_path_for_source(src_project),
            "-comp", genspec.aftereffects_outputcomp,
            "-e", str(last_frame),
            "-OMtemplate", genspec.aftereffects_outputmodule,
            "-reuse",
            "-output", sandbox_output_path          
        ]
        
        if sloelib.SloeConfig.get_option("verbose"):
            print "genspec=%s" % pformat(genspec)
            print "item=%s" % pformat(item)
            print "outputspec=%s" % pformat(outputspec)
        
        logging.info("Executing command %s" % " ".join(command))
        
        p = subprocess.Popen(command, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        (stdout, stderr) = p.communicate()
        if p.returncode != 0:        
            raise sloelib.SloeError("Command failed with return code %d: %s\n%s" % (p.returncode, "".join(stderr), "".join(stdout)))        
        
        if sloelib.SloeConfig.get_option("postrenderabort"):
            logging.info("Aborting due to --postrenderabort flag")
            sys.exit(1)
            
        final_output_path = sloelib.SloeOutputUtil.get_output_path(genspec, item, outputspec)
        
        shutil.move(sandbox_output_path, final_output_path)
            
        sandbox.destroy()
    
        sloelib.SloeOutputUtil.create_output_ini(genspec, item, outputspec)        
    
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

    