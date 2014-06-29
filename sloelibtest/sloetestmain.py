
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



    def tearDown(self):
        SloeTestEnv.inst().destroy_env()


    def test_shuffle(self):
        pass


class SloeTestMain(object):

    def enter(self):
        try:
            suite = unittest.TestLoader().loadTestsFromTestCase(TestCreateTestEnv)
            unittest.TextTestRunner(verbosity=2).run(suite)
        except Exception, e:
            SloeTestEnv.inst().cleanup_env()
            raise
