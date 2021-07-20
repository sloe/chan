#
# Derivied from Google sample code, Apache 2.0 license
#

import httplib
import httplib2
import logging
import os
from pprint import pformat, pprint
import sys
import time

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

from sloelib import SloeError

class SloeYouTubePlaylist(object):
    MAX_RETRIES = 10

    RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError, httplib.NotConnected,
                            httplib.IncompleteRead, httplib.ImproperConnectionState,
                            httplib.CannotSendRequest, httplib.CannotSendHeader,
                            httplib.ResponseNotReady, httplib.BadStatusLine)
    RETRIABLE_STATUS_CODES = (500, 502, 503, 504)

    @classmethod
    def do_insert_playlist(cls, session, spec):
        tags = None
        if "tags" in spec:
            tags = spec["tags"].split(",")

        body=dict(
            snippet=dict(
                title=spec["title"],
                description=spec["description"],
                tags=tags
                ),
            status=dict(
                privacyStatus=spec["privacy"]
            )
        )

        insert_request = session().playlists().insert(
            part=",".join(body.keys()),
            body=body
        )

        return insert_request.execute()




    @classmethod
    def do_read_playlist_item_ids(cls, session, playlist_id, none_if_error=True):

        list_request = session().playlistItems().list(
            maxResults=50,
            part="id,snippet",
            playlistId=playlist_id
        )
        
        ret_ids = []
        total_results = None
        while list_request:
            list_response = list_request.execute()
            for playlistitem in list_response[u"items"]:
                playlistitem_id = playlistitem["id"]
                snippet = playlistitem.get(u"snippet", {})
                resourceId = snippet.get(u"resourceId", {})
                videoId = resourceId.get(u"videoId", "")
                position = snippet.get(u"position", None)
                                                
                ret_ids.append((playlistitem_id, videoId, position))
            if total_results is None:
                pageInfo = list_response.get(u"pageInfo", {})
                total_results = pageInfo.get(u"totalResults", None)
            list_request = session().playlistItems().list_next(list_request, list_response)
        
        if total_results != len(ret_ids) and none_if_error:
            logging.error("Number of items reported for playlist %s (%d) != number of IDs returned (%d)" % (playlist_id, total_results, len(ret_ids)))
            return None
        
        return ret_ids


    @classmethod
    def do_playlist_wipe(cls, session, playlist_id):
        for i in xrange(1000):
            if i > 10:
                raise SloeError("Unable to wipe all entries from playlist %s" % playlist_id)
            playlistitem_ids = cls.do_read_playlist_item_ids(session, playlist_id, none_if_error=False)
            if len(playlistitem_ids) == 0:
                break
            for playlistitem_id in playlistitem_ids:
                cls.do_delete_playlistitem(session, playlistitem_id)


    @classmethod
    def do_delete_playlistitem(cls, session, playlistitem_id):
        delete_request = session().playlistItems().delete(
            id=playlistitem_id
        )
        delete_request.execute()       


    @classmethod
    def do_insert_playlistitem(cls, session, playlist_id, video_id, position):
        body=dict(
            snippet=dict(
                playlistId=playlist_id,
                position=position,
                resourceId=dict(
                    kind="youtube#video",
                    videoId=video_id
                )
            )
        )

        insert_request = session().playlistItems().insert(
            part=",".join(body.keys()),
            body=body
        )

        return insert_request.execute()


    @classmethod
    def do_update_playlistitem(cls, session, playlist_id, playlistitem_id, video_id, position):
        body=dict(
            id=playlistitem_id,
            snippet=dict(
                playlistId=playlist_id,
                position=position,
                resourceId=dict(
                    kind="youtube#video",
                    videoId=video_id
                )
            )
        )

        update_request = session().playlistItems().update(
            part=",".join(body.keys()),
            body=body
        )

        try:
            update_request.execute()
            
        except HttpError, e:
            # It's currently not possible to update a playlistitem with a new video ID.
            # Thie response captures the error and performs a delete and insert instead
            if e.resp.status == 400:
                logging.info("Update failed so will delete and replace")
            else:
                raise

        cls.do_delete_playlistitem(session, playlistitem_id)
        cls.do_insert_playlistitem(session, playlist_id, video_id, position)
