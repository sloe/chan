
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
        self.tempdir = None
        self.treedir = None
        self.env_exists = False


    @classmethod
    def inst(cls):
        if cls.instance is None:
            cls.instance = SloeTestEnv()
        return cls.instance


    def create_env(self):
        if self.tempdir is None:
            self.tempdir = tempfile.mkdtemp(prefix="_sloetest_", dir=".")
        self.treedir = os.path.join(self.tempdir, "test")
        src_tree = sloelib.SloeConfig.get_global("testdataroot")
        shutil.copytree(src_tree, self.treedir)

        sloelib.SloeConfig.set_global("treeroot", self.treedir)
        logging.info("Test directory is %s" % sloelib.SloeConfig.get_global("treeroot"))
        self.env_exists = True


    def cleanup_env(self):
        if self.env_exists:
            self._destroy_env()


    def _destroy_env(self):
        logging.info("Removing test directory %s" % self.tempdir)
        shutil.rmtree(self.tempdir)
        self.env_exists = False


    def has_ae(self):
        return sloelib.SloeConfig.get_global_default("aeprojectdir", "") != ""


    def has_ffprobe(self):
        return sloelib.SloeConfig.get_global_default("ffprobe", "") != ""

