#!/usr/bin/python

import cPickle
import logging
import os
import pprint
import time

import sloelib

class SloeYouTubeItem:
    ID_TAG_PREFIX = u"sloeid="
    def __init__(self, spec):
        self.spec = spec

    def get(self, name):
        return self.spec[name]


    def _set_modified(self):
        self.spec[u"sloemodified"] = True


    def set_sloeid_tag(self, sloeid_tag):
        snippet = self.spec[u"sloevideo"][u"snippet"]
        if snippet.get(u"tags", None) is None:
            snippet[u"tags"] = []

        formed_tag = self.ID_TAG_PREFIX + sloeid_tag

        tag_found = False
        for tag in snippet[u"tags"]:
            if tag.startswith(self.ID_TAG_PREFIX):
                if tag == formed_tag and not tag_found:
                    tag_found = True
                    # Continue so as to remove duplicates
                else:
                    glb_cfg = sloelib.SloeConfig.inst()
                    if sloelib.SloeConfig.get_option("resetsloeid"):
                        logging.warning("Resetting sloeid tag for %s.  Was %s, now %s" % (self.spec[u"title"], tag, formed_tag))
                        snippet[u"tags"].remove(tag)
                        self._set_modified()
                    else:
                        raise sloelib.SloeError("Tag mismatch for %s - %s != %s.  Use --reset-sloeid if required" % (self.spec[u"title"], tag, formed_tag))

        if not tag_found:
            logging.warning("Adding sloeid tag for %s" % self.spec[u"title"])
            snippet[u"tags"].append(formed_tag)
            self._set_modified()

    def update_video_description(self, description):
        snippet = self.spec[u"sloevideo"][u"snippet"]
        if snippet[u"description"] != description:
            snippet[u"description"] = description
            self._set_modified()


    def __repr__(self):
        return "|YouTubeItem|%s" % pformat(self.spec)