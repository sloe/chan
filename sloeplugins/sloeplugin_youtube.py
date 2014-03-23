
import logging
import os
import sys
from pprint import pprint, pformat

import sloelib
from sloeyoutube import SloeYouTubePlaylist, SloeYouTubeSession

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


    def do_item_transfer_job(self, item, transferspec):
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
            remote_id = sloeyoutube.SloeYouTubeUpload.do_upload(youtube_session, youtube_spec)

            remoteitem.update({
                "description": youtube_spec["description"],
                "remote_id": remote_id,
                "remote_url": "http://youtu.be/%s" % remote_id,
                "title": youtube_spec["title"]
            })
            
            remoteitem.verify_creation_data()
            sloelib.SloeOutputUtil.create_remoteitem_ini(item, remoteitem)
            logging.debug("|YouTubeSpec|=%s" % pformat(youtube_spec))
            
        except sloelib.SloeError, e:
            logging.error("Abandoned transfer attempt: %s" % str(e))


    def do_playlist_transfer_job(self, playlist):
        try:
            remoteplaylist = sloelib.SloeOutputUtil.find_remoteplaylist(playlist)
            
            youtube_spec = {}
            
            elements = (
                "description",
                "privacy",
                "tags",
                "title"
            )
            
            for element in elements:
                youtube_spec[element] = sloelib.SloeOutputUtil.substitute_for_remote_playlist(
                    getattr(playlist, 'youtube_' + element), playlist, remoteplaylist)
             
               
            tags = youtube_spec["tags"].split(",")
            tags.append("oarstackremoteitem=%s" % remoteplaylist.uuid)
            youtube_spec["tags"] = ",".join([x.strip() for x in tags])
            logging.info("youtube_spec=%s" % pformat(youtube_spec))
            youtube_session = SloeYouTubeSession("w")
            youtube_playlist = SloeYouTubePlaylist.do_insert_playlist(youtube_session, youtube_spec)

            ordered_items = playlist.get_ordered_items()
            if len(ordered_items) == 0:
                raise SloeError("Playlist %s in empty" % playlist.name)
            
            first_video_youtube_id = ordered_items[0].remote_id

            remoteplaylist.update({
                "description": youtube_spec["description"],
                "remote_id": youtube_playlist["id"],
                "remote_url": "http://www.youtube.com/watch?v=%s&list=%s" % (first_video_youtube_id, youtube_playlist["id"]),
                "title": youtube_spec["title"]
            })
            
            remoteplaylist.verify_creation_data()
            sloelib.SloeOutputUtil.create_remoteplaylist_ini(playlist, remoteplaylist)
            
            for remoteitem in ordered_items:
                self._insert_playlist_item(youtube_session, remoteitem, youtube_playlist["id"])
            
            logging.debug("|YouTubeSpec|=%s" % pformat(youtube_spec))
            
        except KeyboardInterrupt, e: #sloelib.SloeError, e:
            logging.error("Abandoned transfer attempt: %s" % str(e))


    def _insert_playlist_item(self, youtube_session, remoteitem, playlist_youtube_id):
        youtube_spec = dict(
            playlistId=playlist_youtube_id,
            resourceId=dict(
                kind="youtube#video",
                videoId=remoteitem.remote_id
            )
        )
        
        logging.info("youtube_spec=%s" % pformat(youtube_spec))
        playlistitem_remote_id = SloeYouTubePlaylist.do_insert_playlistitem(youtube_session, youtube_spec)
        pass

SloePluginYoutube("youtube")
