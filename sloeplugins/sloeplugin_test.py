
import logging
import os
import sys
from pprint import pprint, pformat
import unittest

import sloelib
import sloelibtest

class SloePluginTest(sloelib.SloeBasePlugIn):

    def command_test(self, params, options):
        logging.info("Test command")
        testmain = sloelibtest.SloeTestMain()
        testmain.enter()


SloePluginTest("test")
