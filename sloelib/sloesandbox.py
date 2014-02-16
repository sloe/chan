
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
            self._sandbox_dir = os.path.join(SloeConfig.get_global().get("global", "sandboxdir"), self.subdir)
        
        if extra is None:
            return self._sandbox_dir
        else:
            return  os.path.join(self._sandbox_dir, extra)
            
            
    def get_lock_filepath(self):
        return self.get_sandbox_path(self.LOCK_FILENAME)
        

    def is_locked(self):
        return os.path.isfile(self.get_lock_filepath())
        
        
    def lock(self):
        if self.is_locked():
            raise SloeError("Sandbox locked - remove '%s' file to continue" %
                           self.get_lock_filepath())
        
        with open(self.get_lock_filepath(), mode="w") as f:
            f.write("%d\n%s (PID=%d) has locked this sandbox" % (os.getpid(), __file__, os.getpid()))
           
           
    def unlock(self):
        if not self.is_locked():
            raise SloeError("Cannot unlock sandbox - not locked (no lock file '%s')" % self.get_lock_filepath())        
        os.unlink(self.get_lock_filepath())
        
        
    def check_and_destroy_locked_sandbox(self):
        if self.is_locked():
            lock_pid = "<invalid>"
            with open(self.get_lock_filepath(), mode="r") as f:
                try:    
                    line = f.readline()
                    lock_pid = int(line)
                except Exception, e:
                    logging.error("Cannot determine PID value from lock file line '%s' (%s)" % (line, str(e)))
            
            running_pids = SloeUtil.get_running_pids()
            if lock_pid in running_pids:
                logging.info("Process holding sandbox lock (PID=%d) is still running" % lock_pid)
            else:
                logging.info("Process holding sandbox lock (PID=%d) is not running - destroying sandbox" % lock_pid)   
                self.destroy()
            
        
    def create(self, files_to_copy):
        sandbox_path = self.get_sandbox_path()
        if not os.path.isdir(sandbox_path):
            os.makedirs(sandbox_path)
            
        if self.is_locked():
            self.check_and_destroy_locked_sandbox()

        self.lock()
        self.filemap = {}
        for src, dest in files_to_copy.iteritems():
            sandbox_dest = os.path.join(sandbox_path, dest)
            self.filemap[src] = dest
            logging.info("Copying file '%s' into sandbox '%s'" % (src, sandbox_dest))
            shutil.copy2(src, sandbox_dest)
            
            
    def destroy(self):
        if not self.is_locked():
            raise SloeError("Cannot destroy sandbox because lock not held")
            
        keepsandbox = SloeConfig.get_global().get_option("keepsandbox")            
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
                
        self.unlock()
