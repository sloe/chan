
import logging
import os
from pprint import pformat, pprint

from sloeconfig import SloeConfig
from sloetrees import SloeTrees
from sloetreeutil import SloeTreeUtil


class SloeExecUtil(object):
    
    @classmethod   
    def do_work(cls, executor, work_list):
        for job in work_list:
            executor.do_job(job)
            
            
    @classmethod
    def extract_common_id(cls, common_id):
        extracted = {}
        for section in common_id.split(","):
            (tag, value) = section.split("=")
            extracted[tag] = value
            
        return extracted
    
    
    @classmethod   
    def get_specs_for_job(cls, jobspec):
        ids = cls.extract_common_id(jobspec.common_id)
        (album, item) = SloeTrees.inst().find_album_and_item(ids["I"])
        outputspec = SloeTreeUtil.find_outputspec(album, ids["O"])
        genspec_uuid = outputspec.get("genspec_uuid", None)
        if not genspec_uuid:
            genspec_name = outputspec.get("genspec_name", None)
            if not genspec_name:
                raise SloeError("OutputSpec %s '%s' missing both genspec_name and genspec_uuid" % (outputspec.uuid, outputspec.name))
            genspec_uuid = SloeTreeUtil.find_genspec_uuid_by_name(album, genspec_name)
            
        genspec = SloeTreeUtil.find_genspec(album, genspec_uuid)
        
        return (genspec, item, outputspec)
        