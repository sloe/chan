
import logging
import os
from pprint import pformat, pprint
import win32api
import win32pdh

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
                path = win32pdh.MakeCounterPath((None, 'process', instance, None, inum, 'ID Process'))
                counter_handle=win32pdh.AddCounter(hq, path) 
                win32pdh.CollectQueryData(hq) #collects data for the counter 
                type, val = win32pdh.GetFormattedCounterValue(counter_handle, win32pdh.PDH_FMT_LONG)
                proc_id = int(val)
                if proc_id != 0:    
                    proc_ids.append(proc_id)
                win32pdh.CloseQuery(hq) 
    
        return proc_ids
 
    
    KNOWN_FRAME_RATES = [
    "23.976",
    "25",
    "29.97",
    "50",
    "59.94"]
    
    @classmethod    
    def get_canonical_frame_rate(cls, framerate_string):
        float_rate = cls.fraction_to_float(framerate_string)
        
        for rate in cls.KNOWN_FRAME_RATES:    
            if abs(float_rate - float(rate)) < 0.01:
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