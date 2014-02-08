#!/usr/bin/python

import cPickle
import logging
import os
import pprint
import time

import sloelib

class SloeYouTubeItem:
  def __init__(self, spec):
    self.spec = spec

  def get(self, name):
    return self.spec[name]

  def __repr__(self):
    return pprint.pformat(self.spec)
