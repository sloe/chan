
import logging
import os
from pprint import pprint

from sloeconfig import SloeConfig
from sloetree import SloeTree

class SloeTrees:
    instance = None

    def __init__(self):
        self.tree = SloeTree.inst()

    @classmethod
    def inst(cls):
        if cls.instance is None:
            cls.instance = SloeTrees()
        return cls.instance


    def get_treepaths(self, primacy):
        glb_cfg = SloeConfig.inst()
        primacies = glb_cfg.get_value("global", "primacies").split(",")
        if primacy not in primacies:
            raise sloelib.SloeError("Invalid primacy %s" % primacy)
        root_dir = glb_cfg.get_value("global", "treeroot")
        retval = {}

        for worth in glb_cfg.get_value("global", "worths").split(","):
            retval[worth] = os.path.join(root_dir, primacy, worth)
        return retval


    def get_treeroot(self, primacy, worth):
        glb_cfg = SloeConfig.inst()
        primacies = glb_cfg.get_value("global", "primacies").split(",")
        if primacy not in primacies:
            raise sloelib.SloeError("Invalid primacy %s" % primacy)        
        worths = glb_cfg.get_value("global", "worths").split(",")
        if worth not in worths:
            raise sloelib.SloeError("Invalid worth %s" % worth)
        
        root_dir = glb_cfg.get_value("global", "treeroot")
        return os.path.join(root_dir, primacy, worth)
        
    def get_tree(self):
        if self.tree is None:
            self._load_tree()
        return self.tree


    @classmethod 
    def walk_albums(cls, album):
        yield album
        for subalbum in album.subalbums:
            for x in cls.walk_albums(subalbum):
                yield x


    def find_album_or_none(self, album_uuid):
        for album in self.walk_albums(self.tree.root_album):
            if album.uuid == album_uuid:
                return album

        return None
    

    def find_album_and_item(self, item_uuid):
        for album in self.walk_albums(self.tree.get_root_album()):
            item = album.item_dict.get(item_uuid)
            if item:
                return (album, item)

        raise SloeError("Item not found for %s" % item_uuid)


    def _load_tree(self):
        self.tree = SloeTree.inst()
        self.tree.make()

