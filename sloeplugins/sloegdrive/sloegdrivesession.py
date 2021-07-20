#!/usr/bin/python

import httplib2
import os
import sys

from googleapiclient.discovery import build
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow

import sloelib

class SloeGDriveSession(object):
    GDRIVE_API_SERVICE_NAME = "drive"
    GDRIVE_API_VERSION = "v2"
    CLIENT_ID = "sloe"

    def __init__(self, access):
        self.gdrive = None
        authtokensroot = sloelib.SloeConfig.inst().get_global('gdriveauthtokensroot')
        self.secrets_file = os.path.join(authtokensroot, "gdrive_secrets.json")
        self.storage_file = os.path.join(authtokensroot, "gdrive_oauth_storage_%s.json" % access)
        if access == "w":
            self.scope = "https://www.googleapis.com/auth/drive.file"
        elif access == "r":
            self.scope = "https://www.googleapis.com/auth/drive.readonly"
        else:
            raise sloelib.SloeError("access must be r or w")

    def __call__(self):
        if self.gdrive is None:
            self._open_session()

        return self.gdrive

    def _open_session(self):
        self.flow = flow_from_clientsecrets(self.secrets_file,
                                            message="Authentication failed",
                                            scope=self.scope)

        storage = Storage(self.storage_file)
        credentials = storage.get()

        if credentials is None or credentials.invalid:
            flags = argparser.parse_args([])
            credentials = run_flow(self.flow, storage, flags)

        self.gdrive = build(self.GDRIVE_API_SERVICE_NAME, self.GDRIVE_API_VERSION,
                             http=credentials.authorize(httplib2.Http()))

