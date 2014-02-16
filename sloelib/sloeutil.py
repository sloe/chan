
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
    
    