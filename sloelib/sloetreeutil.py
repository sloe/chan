
import logging
import os
from pprint import pformat, pprint
import uuid

from sloealbum import SloeAlbum
from sloeconfig import SloeConfig
from sloeerror import SloeError
from sloeitem import SloeItem
from sloetrees import SloeTrees


class SloeTreeUtil(object):
    def __init__(self, tree):
        self.tree = tree
        glb_cfg = SloeConfig.inst()
        self.verbose = sloelib.SloeConfig.get_option("verbose")


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
        parent_album = SloeTrees.inst().find_album_or_none(album.parent_uuid)
        if parent_album:
            for x in cls.walk_parents(parent_album):
                yield x
        yield album
        

    @classmethod 
    def get_parent_outputspecs(cls, album):
        outputspecs = []
        for album in cls.walk_parents(album):
            outputspecs += album.outputspecs

        return outputspecs
    
    
    @classmethod 
    def find_genspec_uuid_by_name(cls, album, genspec_name):
        for album in SloeTreeUtil.walk_parents(album):
            for obj in album.genspecs:
                if obj.name == genspec_name:
                    return obj.uuid
        raise SloeError("GenSpec not found for name '%s'" % genspec_name)
    
    
    @classmethod 
    def find_genspec(cls, album, obj_uuid):
        for album in SloeTreeUtil.walk_parents(album):
            for obj in album.genspecs:
                if obj.uuid == obj_uuid:
                    return obj
                    
        raise SloeError("GenSpec not found for %s" % obj_uuid)
    
    
    @classmethod 
    def find_item(cls, album, obj_uuid):
        for album in SloeTreeUtil.walk_parents(album):
            for obj in album.items:
                if obj.uuid == obj_uuid:
                    return obj
                    
        raise SloeError("Item not found for %s" % obj_uuid)
        
        
    @classmethod 
    def find_outputspec(cls, album, obj_uuid):
        for album in SloeTreeUtil.walk_parents(album):
            for obj in album.outputspecs:
                if obj.uuid == obj_uuid:
                    return obj
                    
        raise SloeError("OutputSpec not found for %s" % obj_uuid)
    


    