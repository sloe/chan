
import logging
import os
import sys
from pprint import pprint, pformat

import sloelib
from . import sloeyoutube

class SloePluginYoutube(sloelib.SloeBasePlugIn):

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
            
            youtube_spec = {
                "filepath": item.get_file_path(),
            }
            
            elements = (
                "category",
                "description",
                "privacy",
                "tags",
                "title"
            )
            
            for element in elements:
                youtube_spec[element] = sloelib.SloeOutputUtil.substitute_for_remote_item(
                    getattr(transferspec, 'youtube_' + element), item, remoteitem, transferspec)
             
               
            tags = youtube_spec["tags"].split(":,")
            tags.append("oarstackremoteitem=%s" % remoteitem.uuid)
            youtube_spec["tags"] = ",".join([x.strip() for x in tags])

            logging.info("youtube_spec=%s" % pformat(youtube_spec))
            youtube_session = sloeyoutube.SloeYouTubeSession("upload")
            remote_id = "test"
            # remote_id = sloeyoutube.SloeYouTubeUpload.do_upload(youtube_session, youtube_spec)

            remoteitem.update({
                "description": youtube_spec["description"],
                "remote_id": remote_id,
                "remote_url": "http://youtu.be/%s" % remote_id,
                "title": youtube_spec["title"]
            })
            
            remoteitem.verify_creation_data()
            # sloelib.SloeOutputUtil.create_remoteitem_ini(item, remoteitem)
            logging.debug("|YouTubeSpec|=%s" % pformat(youtube_spec))
        except sloelib.SloeError, e:
            logging.error("Abandoned transfer attempt: %s" % str(e))


SloePluginYoutube("youtube")
