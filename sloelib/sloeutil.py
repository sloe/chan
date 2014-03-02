
import datetime
import logging
import os
from pprint import pformat, pprint
import socket
import win32api
import win32pdh

# Self-contained utilities - mustn't import anything from sloelib except SloeError
from sloeerror import SloeError

class SloeUtil(object):
    @classmethod
    def get_running_pids(cls):
        # From ActiveState example
        junk, instances = win32pdh.EnumObjectItems(None, None, 'process', win32pdh.PERF_DETAIL_WIZARD)
        proc_ids=[]
        proc_dict={}
        for instance in instances:
            if instance in proc_dict:
                proc_dict[instance] = proc_dict[instance] + 1
            else:
                proc_dict[instance]=0
        for instance, max_instances in proc_dict.items():
            for inum in xrange(max_instances+1):
                hq = win32pdh.OpenQuery() # initializes the query handle
                try:
                    path = win32pdh.MakeCounterPath((None, 'process', instance, None, inum, 'ID Process'))
                    counter_handle=win32pdh.AddCounter(hq, path) 
                    win32pdh.CollectQueryData(hq) #collects data for the counter 
                    type, val = win32pdh.GetFormattedCounterValue(counter_handle, win32pdh.PDH_FMT_LONG)
                    proc_id = int(val)
                    if proc_id != 0:    
                        proc_ids.append(proc_id)
                except Exception, e:
                    logging.error("Error finding running processes (%s)" % str(e))
                finally:    
                    win32pdh.CloseQuery(hq) 
    
        return proc_ids
 
    
    KNOWN_FRAME_RATES = [
    "23.976",
    "25",
    "29.97",
    "50",
    "59.94",
    "119.88"]
    
    @classmethod    
    def get_canonical_frame_rate(cls, framerate_string):
        float_rate = cls.fraction_to_float(framerate_string)
        
        for rate in cls.KNOWN_FRAME_RATES:    
            if abs(float_rate - float(rate)) < 0.04:
                logging.debug("Conforming rate %s (%.4f) to %s" % (framerate_string, float_rate, rate))
                return rate
            
            
        logging.debug("Failed to conform frame rate %s (%.4f)" % (framerate_string, float_rate))        
        return str(float_rate)
    
    
    @classmethod    
    def fraction_to_float(cls, fraction_string):
        split_value = fraction_string.split("/")

        if len(split_value) == 1:
            float_value = float(split_value[0])
        elif len(split_value) == 2:
            float_value = float(split_value[0]) / float(split_value[1])
        else:
            raise SloeError("Cannot determine numerical value from %s" % framerate_string)            
            
        return float_value
    

    @classmethod    
    def is_locked(cls, filepath):
        return os.path.isfile(filepath)
        
        
    @classmethod    
    def lock(cls, filepath):
        if cls.is_locked(filepath):
            raise SloeError("Already locked - remove '%s' file to continue" % filepath)
        
        with open(filepath, mode="w") as f:
            f.write("%s\n%d\n%s on host %s, PID=%d created this lockfile at %s" %
                    (socket.gethostname(), os.getpid(), __file__, socket.gethostname(), os.getpid(),
                     datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%SZ')))
           
           
    @classmethod    
    def unlock(cls, filepath):
        if not cls.is_locked(filepath):
            raise SloeError("Cannot unlock because no lock present (no lock file '%s')" % filepath)        
        os.unlink(filepath)
        

    @classmethod
    def take_lock_if_possible(cls, filepath):
        if not cls.is_locked(filepath):
            return None
        
        lock_hostname = "<invalid>"
        lock_pid = "<invalid>"
        with open(filepath, mode="r") as f:
            try:    
                line = f.readline()
                lock_hostname = line.rstrip()
            except Exception, e:
                logging.error("Cannot determine hostname from lock file line '%s' (%s)" % (line, str(e)))
            try:    
                line = f.readline()
                lock_pid = int(line)
            except Exception, e:
                logging.error("Cannot determine PID value from lock file line '%s' (%s)" % (line, str(e)))

        if lock_hostname != socket.gethostname():
            logging.info("Lock held by another host '%s'" % lock_hostname)
            return "otherhost"
        
        running_pids = SloeUtil.get_running_pids()
        if lock_pid not in running_pids:        
            logging.info("Locked by this host but process holding lock (PID=%d) is not running" % lock_pid)
            os.unlink(filepath)
            return "take"
            
        logging.info("Process holding lock (PID=%d) is still running" % lock_pid)
        return "locked"
        