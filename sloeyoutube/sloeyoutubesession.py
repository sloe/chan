

#!/usr/bin/python

import httplib2
import os
import sys

from apiclient.discovery import build
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow

import sloelib

class SloeYouTubeSession:
  YOUTUBE_API_SERVICE_NAME = "youtube"
  YOUTUBE_API_VERSION = "v3"

  def __init__(self, access):
    self.youtube = None
    self.secrets_file = "client_secrets.json"
    self.storage_file = "oauth_storage_%s.json" % access
    if access == "w":
      self.scope = "https://www.googleapis.com/auth/youtube"
    elif access == "r":
      self.scope = "https://www.googleapis.com/auth/youtube.readonly"
    else:
      raise sloelib.SloeException("access must be r or rw")

  def get_session(self):
    if self.youtube is None:
      self._open_session()

    return self.flow

  def _open_session(self):
    self.flow = flow_from_clientsecrets(self.secrets_file,
      message="Auth failed",
      scope=self.scope)

    storage = Storage(self.storage_file)
    credentials = storage.get()

    if credentials is None or credentials.invalid:
      flags = argparser.parse_args([])
      credentials = run_flow(self.flow, storage, flags)

    self.youtube = build(self.YOUTUBE_API_SERVICE_NAME, self.YOUTUBE_API_VERSION,
      http=credentials.authorize(httplib2.Http()))


