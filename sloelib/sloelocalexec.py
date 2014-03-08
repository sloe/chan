
import logging
import os
from pprint import pformat, pprint

from sloeconfig import SloeConfig
from sloeerror import SloeError
from sloeexecutil import SloeExecUtil
from sloepluginmanager import SloePlugInManager

class SloeLocalExec(object):
    def __init__(self, tree):
        self.tree = tree
        
        
    def do_job(self, jobspec):
        print "J=%s" % pformat(jobspec)
        if jobspec.type == "renderjob":
            genspec, item, outputspec = SloeExecUtil.get_specs_for_render_job(jobspec)
    
            if genspec.gen_type == "aftereffects":
                SloePlugInManager.inst().call_plugin(
                    "aftereffects",
                    "do_render_job",
                    genspec=genspec,
                    item=item,
                    outputspec=outputspec)
        elif jobspec.type == "transferjob":
            if jobspec.transfer_type == "youtube":
                item, transferspec = SloeExecUtil.get_specs_for_transfer_job(jobspec)
                SloePlugInManager.inst().call_plugin(
                    "youtube",
                    "do_transfer_job",
                    item=item,
                    transferspec=transferspec)        
            
            
        
            