#
# Derivied from Google sample code, Apache 2.0 license
#

import httplib
import httplib2
import logging
import os
import sys
import time

from apiclient.discovery import build
from apiclient.errors import HttpError
from apiclient.http import MediaFileUpload

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
    def do_insert_playlistitem(cls, session, spec):
        body=dict(
            snippet=dict(
                playlistId=spec["playlistId"],
                resourceId=spec["resourceId"]
                )
        )

        insert_request = session().playlistItems().insert(
            part=",".join(body.keys()),
            body=body
        )

        return insert_request.execute()
