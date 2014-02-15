
import logging
import os
from pprint import pformat, pprint

from sloeconfig import SloeConfig
from sloeerror import SloeError
from sloeexecutil import SloeExecUtil


class SloeLocalExec(object):
    def __init__(self, tree):
        self.tree = tree
        
        
    def do_job(self, jobspec):
        print "J=%s" % pformat(jobspec)
        genspec, item, outputspec = SloeExecUtil.get_specs_for_job(jobspec)
        print "genspec=%s" % pformat(genspec)
        print "item=%s" % pformat(item)
        print "outputspec=%s" % pformat(outputspec)
                        
            