
import logging
import os
import sys
from pprint import pprint, pformat

import sloelib
from .sloegdrive.sloegdrivefinder import SloeGDriveFinder
from .sloegdrive.sloegdrivesession import SloeGDriveSession

class SloePluginGDrive(sloelib.SloeBasePlugIn):

    def __init__(self, *params):
        sloelib.SloeBasePlugIn.__init__(self, *params)


    def command_gdriveauth(self, params, options):
        session_r = SloeGDriveSession("r")
        session_r()


    def command_gdrivefind(self, params, options):
        finder = SloeGDriveFinder()
        for find_str in params:
            results = finder.find(find_str, options.exact)
            pprint(results)


SloePluginGDrive("gdrive")
