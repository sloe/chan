
import logging
import os
import sys
from pprint import pprint, pformat

import sloelib
from sloeyoutube import SloeYouTubePlaylist, SloeYouTubeSession, SloeYouTubeUpload

class SloePluginYoutube(sloelib.SloeBasePlugIn):

    def command_youtubeauth(self, params, options):
        session_r = SloeYouTubeSession("r")
        session_r()
        session_w = SloeYouTubeSession("w")
        session_w()    
        session_upload = SloeYouTubeSession("upload")
        session_upload()


    def command_youtubedumptree(self, params, options):
        session_r = SloeYouTubeSession("r")
        tree = SloeYouTubeTree(session_r)
        tree.read()
        print tree



    def _get_youtube_spec_for_item(self, item, remoteitem, transferspec):
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

        return youtube_spec
    

    def do_item_transfer_job(self, item, transferspec):
        try:
            remoteitem = sloelib.SloeOutputUtil.find_remoteitem(item, transferspec)
            
            youtube_spec = self._get_youtube_spec_for_item(item, remoteitem, transferspec)
            
            logging.debug("youtube_spec=%s" % pformat(youtube_spec))
            youtube_session = SloeYouTubeSession("upload")
            remote_id = SloeYouTubeUpload.do_upload(youtube_session, youtube_spec)

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


    def do_update_items_job(self, remoteitem_uuids):
        session_w = SloeYouTubeSession("w")
        for remoteitem_uuid in remoteitem_uuids:
            try:
                remoteitem = sloelib.SloeTreeNode.get_object_by_uuid(remoteitem_uuid)
                self._update_remote_item(session_w, remoteitem)
    
            except sloelib.SloeError, e:
                logging.error("Abandoned transfer attempt: %s" % str(e))


    def _update_remote_item(self, session_w, remoteitem):
        ids = sloelib.SloeUtil.extract_common_id(remoteitem.common_id)        
        item = sloelib.SloeTreeNode.get_object_by_uuid(ids["I"])
        transferspec = sloelib.SloeTreeNode.get_object_by_uuid(ids["T"])
        youtube_spec = self._get_youtube_spec_for_item(item, remoteitem, transferspec)
        
        logging.debug("youtube_spec=%s" % pformat(youtube_spec))    
        remote_id = SloeYouTubeUpload.do_item_update(session_w, remoteitem.remote_id, youtube_spec)
        

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
                    playlistitem_id, videoId, position = remote_playlistitems[i]
                    if videoId == ordered_items[i].remote_id and position == i:
                        logging.info("%sRemote item OK: %s" % (prefix, ordered_items[i].title))                        
                    else:
                        # Item is both local and remote, so operation is update
                        logging.info("%sUpdating remote id %s item '%s'" % (prefix, playlistitem_id, ordered_items[i].name))
                        SloeYouTubePlaylist.do_update_playlistitem(youtube_session, youtube_playlistid, playlistitem_id, ordered_items[i].remote_id, i)
                elif i < len(ordered_items):
                    # Item is local but not remote, so operation is insert
                    logging.info("%sInserting item '%s'" % (prefix, ordered_items[i].name))
                    SloeYouTubePlaylist.do_insert_playlistitem(youtube_session, youtube_playlistid, ordered_items[i].remote_id, i)
                elif i < len(remote_playlistitems):
                    # Item is remote but not local, so operation is delete
                    playlistitem_id, videoId, position = remote_playlistitems[i]
                    logging.info("%sDeleting item remote id %s" % (prefix, playlistitem_id))
                    SloeYouTubePlaylist.do_delete_playlistitem(youtube_session, playlistitem_id)
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
