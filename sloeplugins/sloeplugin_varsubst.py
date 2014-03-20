
import logging
import os
import sys
from pprint import pprint, pformat

import sloelib

class SloePluginVarSubst(sloelib.SloeBasePlugIn):
    
    def varsubst_closest(self, params):
        if len(params) != 1:
            raise sloelib.SloeError("closest() requires 1 parameter, %d given" % len(params))
        for value in params[0]:
            if value is not None and value != "":
                return value
        return ""


    def varsubst_join(self, params):
        if len(params) < 2:
            raise sloelib.SloeError("join() requires at least 2 parameters, %d given" % len(params))
        joiners = params[0]
        if len(joiners) == 0:
            raise sloelib.SloeError("Join: at least one joining element must be given")
        ret_str = ""
        for param in params[1:]:
            for i, to_join in enumerate(param):
                if to_join is not None and to_join != "":
                    if len(ret_str) != 0:
                        ret_str += joiners[min(i, len(joiners) - 1)]
                    ret_str += to_join
        return ret_str
        

SloePluginVarSubst("varsubst")
