
import logging
import os
from pprint import pprint, pformat
import shutil
import tempfile

import sloelib

class SloeTestEnv(object):
    instance = None

    def __init__(self):
        self.valid = False
        self.treedir = None
        self.env_exists = False


    @classmethod
    def inst(cls):
        if cls.instance is None:
            cls.instance = SloeTestEnv()
        return cls.instance


    def create_env(self):
        if self.treedir is None:
            self.treedir = tempfile.mkdtemp(prefix="_test", dir=".")
        logging.info("Tree directory is %s" % self.treedir)
        self.env_exists = True


    def cleanup_env(self):
        if self.env_exists:
            self.destroy_env()


    def destroy_env(self):
        shutil.rmtree(self.treedir)
        self.env_exists = False
