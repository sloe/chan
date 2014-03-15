
import logging
import os
import sys
from pprint import pprint, pformat

import sloelib
from . import sloeyoutube

class SloePluginYoutube(sloelib.SloeBasePlugIn):
    def __init__(self, *params):
        self.methods = [
            self.do_transfer_job
        ]
        sloelib.SloeBasePlugIn.__init__(self, *params)
        

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
        

        try:
            remoteitem = sloelib.SloeOutputUtil.find_remoteitem(item, transferspec)
            tags = transferspec.get("tags", []) + ["OARSTACKID:I=%s,R=%s,T=%s" % (item.uuid, remoteitem.uuid, transferspec.uuid)]
            
            title = sloelib.SloeOutputUtil.substitute_for_remote_item(transferspec.title_merge, item, remoteitem, transferspec)
            description = sloelib.SloeOutputUtil.substitute_for_remote_item(transferspec.description_merge, item, remoteitem, transferspec)
            youtube_spec = {
                "category": "17",
                "description": description,
                "filepath": item.get_file_path(),
                "privacy": "unlisted",
                "tags": tags,
                "title": title
            }
            logging.info("youtube_spec=%s" % pformat(youtube_spec))
            youtube_session = sloeyoutube.SloeYouTubeSession("upload")
            remote_id = "test"
            # remote_id = sloeyoutube.SloeYouTubeUpload.do_upload(youtube_session, youtube_spec)

            remoteitem.update({
                "description": description,
                "remote_id": remote_id,
                "remote_url": "http://youtu.be/%s" % remote_id,
                "title": title         
            })
            
            remoteitem.verify_creation_data()
            # sloelib.SloeOutputUtil.create_remoteitem_ini(item, remoteitem)
        except sloelib.SloeError, e:
            logging.error("Abandoned transfer attempt: %s" % str(e))


SloePluginYoutube("youtube")
