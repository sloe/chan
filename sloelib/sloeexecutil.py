
import logging
import os
from pprint import pformat, pprint

from sloeconfig import SloeConfig
from sloetrees import SloeTrees
from sloetreeutil import SloeTreeUtil
from sloeutil import SloeUtil


class SloeExecUtil(object):
    
    @classmethod   
    def do_work(cls, executor, work_list):
        for job in work_list:
            executor.do_job(job)
    
    
    @classmethod   
    def get_specs_for_render_job(cls, jobspec):
        ids = SloeUtil.extract_common_id(jobspec.common_id)
        (album, item) = SloeTrees.inst().find_album_and_item(ids["I"])
        outputspec = SloeTreeUtil.find_outputspec(ids["O"])
        genspec_uuid = SloeTreeUtil.get_genspec_uuid_for_outputspec(outputspec)
            
        genspec = SloeTreeUtil.find_genspec(genspec_uuid)
        
        return (genspec, item, outputspec)
        
    
    @classmethod   
    def get_specs_for_transfer_job(cls, jobspec):
        ids = SloeUtil.extract_common_id(jobspec.common_id)
        (album, item) = SloeTrees.inst().find_album_and_item(ids["I"])
        transferspec = SloeTreeUtil.find_transferspec(album, ids["T"])
        
        return (item, transferspec)
        