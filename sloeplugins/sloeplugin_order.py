
import logging
import os
import re
import sys
from pprint import pprint, pformat

import sloelib

class SloePluginOrder(sloelib.SloeBasePlugIn):  

    initial_number_regex = re.compile(r'\s*([-+0-9.]+)')
    
    def _calc_initial_number(self, obj):
        match = initalial_number_regex.match(obj.name)
        if match:
            initial_number = float(match.group(1))
        else:
            logging.warn("Cannot calculate initial number from oject name '%s'" % obj.name)
            initial_number = 0.0
        obj.set_value("_order_initial_number", initial_number)
        return initial_number
            
    
    def order_initial_number(self, obj1, obj2):
        numbers = []
        for obj in obj1, obj2:
            initial_number = obj.get("_order_initial_number", None)
            if initial_number is None:
                initial_number = self._calc_initial_number(obj)
            

SloePluginOrder("order")
    