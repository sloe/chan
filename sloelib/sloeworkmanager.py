
import logging
import os
from pprint import pformat, pprint
import uuid

from sloealbum import SloeAlbum
from sloeconfig import SloeConfig
from sloeerror import SloeError
from sloeitem import SloeItem
from sloeoutputspec import SloeOutputSpec
from sloetreeutil import SloeTreeUtil


class SloeWorkManager(object):
    def __init__(self, tree):
        self.tree = tree    


    def get_work_for_item(self, album, item, outputspec):
       return []


    def get_all_work(self, tree):
        work = []
        root_album = self.tree.get_root_album()
        for subtree, album, items in SloeTreeUtil.walk_items(root_album):
            print "%s Album: %s '%s' (%s)" % (album.uuid, album.name, album.title, album._location.replace("\\", "/"))
            outputspecs = SloeTreeUtil.get_parent_outputspecs(album)
            print "len outputspecs %d" % len(outputspecs)
            for outputspec in outputspecs:
                print "%s OutputSpec: %s" % (outputspec.uuid, outputspec.name)
                
                for item in items:
                    work += self.get_work_for_item(album, item, outputspec)                    

        pprint(work)
        