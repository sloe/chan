
import codecs
import datetime
import logging
import os
from pprint import pformat, pprint
import re
import socket
import types
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
            if abs(float_rate - float(rate)) < 0.2:
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
        
        
    @classmethod
    def substitute_vars(cls, input_string, replacements):
        value = input_string[:]
        for i in xrange(10000):
            if i == 1000:
                raise SloeError("Recursion in variable substitution for %s" % input_string)
                
            match = re.match(r'(.*){([\w.]+)}(.*)', value)
            if not match:
                break
            name = match.group(2)
            if name not in replacements:
                raise SloeError("No substitution variable {%s} - options are %s" % (name, ",".join(replacements.keys())))
            value = match.group(1) + replacements[name] + match.group(3)
   
        return value
    
    
    @classmethod
    def substitute_from_node_list(cls, input_string, node_name, node_or_nodes):
        if isinstance(node_or_nodes, types.ListType) or isinstance(node_or_nodes, types.TupleType):
            nodes = node_or_nodes
        else:
            nodes = (node_or_nodes,)
            
        value = input_string[:]
        search_regexp = re.compile(r'(.*){([^}]*)' + node_name + r'\.(\w+)}(.*)')
        
        for i in xrange(10000):
            if i == 1000:
                raise SloeError("Recursion in variable substitution for %s" % input_string)
            match = search_regexp.match(value)
            if not match:
                break
            subst = None
            prefix = match.group(2)
            name = match.group(3)
            name_plus_split = prefix.split("+")
            if len(name_plus_split) == 2:
                subst_array = []
                for node in nodes:
                    subst = node.get(name, "")
                    if subst != "":
                        subst_array.append(subst)
                subst = name_plus_split[0].join(subst_array)
            elif prefix == ">":
                for node in reversed(nodes):
                    subst = node.get(name, None)
                    if subst is not None:
                        break
            elif prefix == "<":
                for node in nodes:
                    subst = node.get(name, None)
                    if subst is not None:
                        break                
            else:
                for node in nodes:
                    subst = node.get(name, None)
                    if subst is not None:
                        break
            if subst is None:
                raise SloeError("No substitution variable {%s%s.%s}" % (prefix, node_name, name))
            # logging.debug("Substituted %s for {%s%s.%s}" % (subst, prefix, node_name, name))
            value = match.group(1) + subst + match.group(4)
   
        return value
            
            
    @classmethod
    def extract_common_id(cls, common_id):
        extracted = {}
        for section in common_id.split(","):
            (tag, value) = section.split("=")
            extracted[tag] = value
            
        return extracted


    @classmethod
    def get_unicode_file_content(cls, full_path):
        content = ""
        with open(full_path, 'rb') as f:
            content = f.read()
           
           
        for encoding in ("utf-16", "utf-8-sig", "latin-1"):
            try:
                return codecs.decode(content, encoding)
            except UnicodeDecodeError:
                pass
        raise SloeError("Unable to decode text file '%s'" % full_path)


    @classmethod
    def get_unicode_file_lines(cls, full_path):
        decoded = cls.get_unicode_file_content(full_path)
        return decoded.splitlines()
