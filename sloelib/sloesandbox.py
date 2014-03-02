
import logging
import os
from pprint import pprint, pformat
import re
import shutil
import uuid

from sloeconfig import SloeConfig
from sloeerror import SloeError
from sloetreenode import SloeTreeNode
from sloeutil import SloeUtil

class SloeSandbox(object):
    LOCK_FILENAME = "lock.txt"
    def __init__(self, subdir):
        self.filemap = {}
        self.subdir = subdir
        self._sandbox_dir = None
        
    
    
    def get_sandbox_path(self, extra=None):
        if self._sandbox_dir is None:
            self._sandbox_dir = os.path.join(SloeConfig.inst().get_value("global", "sandboxdir"), self.subdir)
        
        if extra is None:
            return self._sandbox_dir
        else:
            return  os.path.join(self._sandbox_dir, extra)
  
  
    def get_sandbox_path_for_source(self, src):
        return self.get_sandbox_path(self.filemap[src])
            
            
    def get_lock_filepath(self):
        return self.get_sandbox_path(self.LOCK_FILENAME)
        
        
    def check_and_destroy_locked_sandbox(self):
        take_result = SloeUtil.take_lock_if_possible(self.get_lock_filepath())
        if take_result == "take":
            SloeUtil.lock(self.get_lock_filepath())
            self.destroy()
            
        
    def create(self, files_to_copy):
        sandbox_path = self.get_sandbox_path()
        if not os.path.isdir(sandbox_path):
            os.makedirs(sandbox_path)
            
        if SloeUtil.is_locked(self.get_lock_filepath()):
            self.check_and_destroy_locked_sandbox()

        SloeUtil.lock(self.get_lock_filepath())
        self.filemap = {}
        for src, dest in files_to_copy.iteritems():
            sandbox_dest = os.path.join(sandbox_path, dest)
            self.filemap[src] = dest
            logging.info("Copying file '%s' (%.1fMB) into sandbox '%s'" % (src, float(os.path.getsize(src)) / 2 ** 20, sandbox_dest))
            shutil.copy2(src, sandbox_dest)
            
            
    def destroy(self):
        if not SloeUtil.is_locked(self.get_lock_filepath()):
            raise SloeError("Cannot destroy sandbox because lock not held")
            
        keepsandbox = SloeConfig.inst().get_option("keepsandbox")            
        if not keepsandbox:
            sandbox_path = self.get_sandbox_path()
            for dirpath, dirnames, filenames in os.walk(sandbox_path, topdown=False):
                for f in filenames:
                    delete_path = os.path.join(dirpath, f)
                    if delete_path != self.get_lock_filepath():
                        logging.info("Deleting sandbox file '%s'" % delete_path)                
                        os.unlink(delete_path)
                for d in dirnames:
                    delete_path = os.path.join(dirpath, d)
                    logging.info("Deleting sandbox directory '%s'" % delete_path) 
                    os.rmdir(delete_path)
                
        SloeUtil.unlock(self.get_lock_filepath())
