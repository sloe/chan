
import logging
import os
import sys
from pprint import pprint, pformat

import sloelib
from .sloegdrive import sloegdrivesession

class SloePluginGDrive(sloelib.SloeBasePlugIn):

    def __init__(self, *params):
        sloelib.SloeBasePlugIn.__init__(self, *params)


    def command_gdriveauth(self, params, options):
        session_r = sloegdrivesession.SloeGDriveSession("r")
        session_r()


SloePluginGDrive("gdrive")
