
import logging
import os
from pprint import pprint, pformat
import random
import unittest

import sloelib

from sloetestenv import SloeTestEnv

class TestCreateTestEnv(unittest.TestCase):

    def setUp(self):
        SloeTestEnv.inst().create_env()
        self.treeroot = sloelib.SloeConfig.get_global("treeroot")


    def test_directory_exists(self):
        self.treeroot = sloelib.SloeConfig.get_global("treeroot")
        testconfig = os.path.join(self.treeroot, "testconfig.cfg")
        self.assertTrue(os.path.isdir(self.treeroot))
        self.assertTrue(os.path.isfile(testconfig))


    def test_remotes_exist(self):
        if SloeTestEnv.inst().has_ae():
            aeprojectdir = sloelib.SloeConfig.get_global("aeprojectdir")
            self.assertTrue(os.path.isdir(aeprojectdir))
            logging.info("aeprojectdir exists at %s" % os.path.abspath(aeprojectdir))
        else:
            logging.info("aeprojectdir not present so not testing AE")

        if SloeTestEnv.inst().has_ffprobe():
            ffprobe = sloelib.SloeConfig.get_global("ffprobe")
            self.assertTrue(os.path.isfile(ffprobe))
            logging.info("ffprobe exists at %s" % os.path.abspath(ffprobe))
        else:
            logging.info("ffprobe not present so not testing")


    def tearDown(self):
        self.assertTrue(os.path.isdir(self.treeroot))
        SloeTestEnv.inst().cleanup_env()
        self.assertFalse(os.path.isdir(self.treeroot))
        SloeTestEnv.inst().cleanup_env()
        self.assertFalse(os.path.isdir(self.treeroot))


class SloeTestMain(object):

    def enter(self):
        try:
            suite = unittest.TestLoader().loadTestsFromTestCase(TestCreateTestEnv)
            unittest.TextTestRunner(verbosity=2).run(suite)
        finally:
            SloeTestEnv.inst().cleanup_env()

