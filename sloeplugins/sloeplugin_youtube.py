
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


    def do_transfer_job(self, item, transferspec):
        session = sloeyoutube.SloeYouTubeSession("upload")
        spec = {
            "category": "17",
            "description": "Sloecoach test video (auto)",
            "filepath": item.get_file_path(),
            "privacy": "unlisted",
            "title": item.name
        }
        try:            
            remote_id = sloeyoutube.SloeYouTubeUpload.do_upload(session, spec)
            
            remote_url = "http://youtu.be/%s" % remote_id
            sloelib.SloeOutputUtil.create_remoteitem_ini(item, transferspec, 
                                                        remote_id, remote_url)
        except Exception, e:
            logging.error("Abandoned transfer attempt: %s" % str(e))


    @classmethod
    def register(cls):
        obj = SloePluginYoutube()
        spec = {
            "methods": {
                "command_youtubeauth" : cls.command_youtubeauth,
                "command_youtubedumptree" : cls.command_youtubedumptree,
                "do_transfer_job" : cls.do_transfer_job              
            },
            "object": obj
        }
        sloelib.SloePlugInManager.inst().register_plugin("youtube", spec)
        

SloePluginYoutube.register()
