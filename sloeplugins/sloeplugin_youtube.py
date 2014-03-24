
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
            ordered_items = playlist.get_ordered_items()
            if len(ordered_items) == 0:
                raise SloeError("Playlist %s in empty" % playlist.name)

            remoteplaylist = sloelib.SloeOutputUtil.find_remoteplaylist(playlist)
            
            youtube_session = SloeYouTubeSession("w")            
            if remoteplaylist.get("remote_id", None) is not None:
                youtube_playlistid = remoteplaylist.remote_id
                remote_playlistitems = self._read_existing_playlist(youtube_session, youtube_playlistid)
            else:                
                remote_playlistitems = []
                
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
                youtube_playlist = SloeYouTubePlaylist.do_insert_playlist(youtube_session, youtube_spec)

                first_video_youtube_id = ordered_items[0].remote_id
    
                remoteplaylist.update({
                    "description": youtube_spec["description"],
                    "remote_id": youtube_playlist["id"],
                    "remote_url": "http://www.youtube.com/watch?v=%s&list=%s" % (first_video_youtube_id, youtube_playlist["id"]),
                    "title": youtube_spec["title"]
                })
                
                remoteplaylist.verify_creation_data()
                sloelib.SloeOutputUtil.create_remoteplaylist_ini(playlist, remoteplaylist)
                
                youtube_playlistid = youtube_playlist["id"]            
            
            #SloeYouTubePlaylist.do_playlist_wipe(youtube_session, youtube_playlistid)
            #remote_playlistitems = []
            for i in xrange(max(len(ordered_items), len(remote_playlistitems))):
                prefix = "At position %d: " % (i+1)
                if i < len(ordered_items) and i < len(remote_playlistitems):
                    # Item is both local and remote, so operation is update
                    logging.info("%sUpdating remote id %s item '%s'" % (prefix, remote_playlistitems[i], ordered_items[i].name))
                    SloeYouTubePlaylist.do_update_playlistitem(youtube_session, youtube_playlistid, remote_playlistitems[i], ordered_items[i].remote_id, i)
                elif i < len(ordered_items):
                    # Item is local but not remote, so operation is insert
                    logging.info("%sInserting item '%s'" % (prefix, ordered_items[i].name))
                    SloeYouTubePlaylist.do_insert_playlistitem(youtube_session, youtube_playlistid, ordered_items[i].remote_id, i)
                elif i < len(remote_playlistitems):
                    # Item is remote but not local, so operation is delete
                    logging.info("%sDeleting item remote id %s" % (prefix, remote_playlistitems[i]))
                    SloeYouTubePlaylist.do_delete_playlistitem(youtube_session, remote_playlistitems[i])
                else:
                    raise SloeError("Logical error")
            
        except sloelib.SloeError, e:
            logging.error("Abandoned transfer attempt: %s" % str(e))


    def _read_existing_playlist(self, youtube_session, playlist_youtube_id):
        playlistitem_ids = SloeYouTubePlaylist.do_read_playlist_item_ids(youtube_session, playlist_youtube_id)
        if playlistitem_ids is None:
            SloeYouTubePlaylist.do_playlist_wipe(youtube_session, playlist_youtube_id)
            playlistitem_ids = []
        return playlistitem_ids
    

SloePluginYoutube("youtube")
