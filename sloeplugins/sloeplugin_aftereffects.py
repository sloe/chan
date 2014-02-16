
import logging
import os
from pprint import pformat, pprint
import sloelib

class SloePluginAfterEffects(object):
    instance = None
    def __init__(self):
        pass
    
    def do_render_job(self, genspec, item, outputspec):
        logging.info("Performing render job for '%s'" % item.name)
        print "genspec=%s" % pformat(genspec)
        print "item=%s" % pformat(item)
        print "outputspec=%s" % pformat(outputspec)    
    
    
    @classmethod
    def register(cls):
        obj = SloePluginAfterEffects()
        spec = {
            "methods": {
                "do_render_job" : cls.do_render_job
            },
            "object": obj
        }
        sloelib.SloePlugInManager.inst().register_plugin("aftereffects", spec)
        

SloePluginAfterEffects.register()

    