
import logging
import os
import sys
from pprint import pprint, pformat

import sloelib
from . import sloeyoutube

class SloePluginYoutube(object):

    def command_youtubeauth(self, params, options):
        session_r = sloeyoutube.SloeYouTubeSession("r")
        session_r()
        session_w = sloeyoutube.SloeYouTubeSession("w")
        session_w()    


    def command_youtubedumptree(self, params, options):
        session_r = sloeyoutube.SloeYouTubeSession("r")
        tree = sloeyoutube.SloeYouTubeTree(session_r)
        tree.read()
        print tree


    @classmethod
    def register(cls):
        obj = SloePluginYoutube()
        spec = {
            "methods": {
                "command_youtubeauth" : cls.command_youtubeauth,
                "command_youtubedumptree" : cls.command_youtubedumptree
            },
            "object": obj
        }
        sloelib.SloePlugInManager.inst().register_plugin("youtube", spec)
        

SloePluginYoutube.register()
