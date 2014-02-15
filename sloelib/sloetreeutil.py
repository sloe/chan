
import logging
import os
from pprint import pformat, pprint
import uuid

from sloealbum import SloeAlbum
from sloeconfig import SloeConfig
from sloeerror import SloeError
from sloeitem import SloeItem

class SloeTreeUtil(object):
    def __init__(self, tree):
        self.tree = tree
        glb_cfg = SloeConfig.get_global()
        self.verbose = glb_cfg.get_option("verbose")


    def print_ls(self):
        root_album = self.tree.get_root_album()
        for subtree, album, items in self.walk_items(root_album):
            indent = "  " * subtree.count("/")
            try:
                print "%s%sAlbum: %s '%s' (%s)" % (album.uuid, indent, album.name, album.title, album._location.replace("\\", "/"))
                if self.verbose:
                    pprint(album._d)
                for item in items:
                    item_spec = ("%sx%s %sFPS %.2fs %.1fMB" %
                                 (item.video_width, item.video_height, item.video_avg_frame_rate, float(item.video_duration), float(item.video_size) / 2**20))
                    print "%s%s %s (%s %s)" % (item.uuid, indent, item.name, os.path.splitext(item.leafname)[1], item_spec)
                    if self.verbose:
                        pprint(item._d)
    
                for obj in album.genspecs:
                    print "%s%sGenSpec: %s" % (obj.uuid, indent, obj.name)
                    if self.verbose:
                        pprint(obj._d)
    
                for obj in album.outputspecs:
                    print "%s%sOutputSpec: %s" % (obj.uuid, indent, obj.name)
                    if self.verbose:
                        pprint(obj._d)
    
            except Exception, e:
                logging.error("Missing attribute for %s" % album.name)
                raise e
        
    @classmethod 
    def walk_items(cls, album, subtree=[]):
        new_subtree = subtree + [album.name]
        
        yield ("/".join(new_subtree), album, album.items)
        for subalbum in album.subalbums:
            for x in cls.walk_items(subalbum, new_subtree):
                yield x
                
                
    @classmethod
    def walk_parents(cls, album):
        if album.parent_album:
            for x in cls.walk_parents(album.parent_album):
                yield x
        yield album
        

    @classmethod 
    def get_parent_outputspecs(cls, album):
        outputspecs = []
        for album in cls.walk_parents(album):
            outputspecs += album.outputspecs

        return outputspecs
    