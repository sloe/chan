#
# Derivied from Google sample code, Apache 2.0 license
#

import httplib
import httplib2
import logging
import os
import sys
import time

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

import sloelib

from sloeyoutubeitem import SloeYouTubeItem

class SloeYouTubeUpload(object):
    MAX_RETRIES = 10

    RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError, httplib.NotConnected,
                            httplib.IncompleteRead, httplib.ImproperConnectionState,
                            httplib.CannotSendRequest, httplib.CannotSendHeader,
                            httplib.ResponseNotReady, httplib.BadStatusLine)
    RETRIABLE_STATUS_CODES = (500, 502, 503, 504)


    @classmethod
    def do_item_update(cls, session, video_id, spec):
        tags = None
        if "tags" in spec:
            tags = spec["tags"].split(",")

        body=dict(
            id=video_id,
            snippet=dict(
                title=spec["title"],
                description=spec["description"],
                tags=tags,
                categoryId=spec["category"]
                ),
            status=dict(
                privacyStatus=spec["privacy"]
            )
        )

        update_request = session().videos().update(
            part="snippet,status",
            body=body)
        
        result = update_request.execute()
        return result
        


    @classmethod
    def do_upload(cls, session, spec):
        if len(spec["title"]) > 100:
            raise sloelib.SloeError("Upload failure: Title '%s' is too long (%d)" % (spec["title"], len(spec["title"])))
            
        tags = None
        if "tags" in spec:
            tags = spec["tags"].split(",")

        body=dict(
            snippet=dict(
                title=spec["title"],
                description=spec["description"],
                tags=tags,
                categoryId=spec["category"]
                ),
            status=dict(
                privacyStatus=spec["privacy"]
            )
        )

        insert_request = session().videos().insert(
            part=",".join(body.keys()),
            body=body,
            media_body=MediaFileUpload(spec["filepath"], chunksize=-1, resumable=True)
        )

        return cls.resumable_upload(insert_request)


    @classmethod
    def resumable_upload(cls, insert_request):
        response = None
        error_message = None
        retry = 0
        try:
            orig_httplib2_retries = httplib2.RETRIES
            httplib2.RETRIES = 1 # 1 -> no retries, just a single attempt
            while response is None:
                try:
                    logging.info("Uploading file...")
                    status, response = insert_request.next_chunk()
                    if 'id' in response:
                        logging.info("Video id '%s' was successfully uploaded." % response["id"])
                        return response["id"]
                    else:
                        error_message = "The upload failed with an unexpected response: %s" % response
                except HttpError, e:
                    if e.resp.status in cls.RETRIABLE_STATUS_CODES:
                        error_message = "A retriable HTTP error %d occurred:\n%s" % (e.resp.status,
                                                                             e.content)
                    else:
                        raise sloelib.SloeError("Upload failure: %s (%s)" % (str(e), str(e.content)))
                    
                except cls.RETRIABLE_EXCEPTIONS, e:
                    error_message = "A retriable error occurred: %s" % e
    
                if error_message is not None:
                    logging.error(error_message)
                    if retry >= cls.MAX_RETRIES:
                        raise sloelib.SloeError("Upload failed. Abandoning after %d retries" % retry)
                    retry += 1
    
                    max_sleep = 2 ** retry
                    sleep_seconds = max_sleep
                    logging.info("Sleeping %.1f seconds and then retrying..." % sleep_seconds)
                    time.sleep(sleep_seconds)
                    
        finally:
            httplib2.RETRIES = orig_httplib2_retries
            
