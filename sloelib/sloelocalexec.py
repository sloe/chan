
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
                if jobspec.payload_type == "item":                    
                    item, transferspec = SloeExecUtil.get_specs_for_item_transfer_job(jobspec)
                    SloePlugInManager.inst().call_plugin(
                        "youtube",
                        "do_item_transfer_job",
                        item=item,
                        transferspec=transferspec)
                elif jobspec.payload_type == "playlist":                    
                    playlist = SloeExecUtil.get_specs_for_playlist_transfer_job(jobspec)
                    SloePlugInManager.inst().call_plugin(
                        "youtube",
                        "do_playlist_transfer_job",
                        playlist=playlist)
                else:
                    raise SloeError("Unknown youtube transfer job payload type %s" % jobspec.payload_type)
            else:
                raise SloeError("Unknown youtube transfer type %s" % jobspec.transfer_type)                       
        else:
            raise SloeError("Unknown jobspec type %s" % jobspec.type)            
            
        
            