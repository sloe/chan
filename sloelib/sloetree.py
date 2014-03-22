
import logging
import os
import re
from pprint import pformat, pprint
import string
import uuid

from sloealbum import SloeAlbum
from sloeconfig import SloeConfig
from sloeerror import SloeError
from sloegenspec import SloeGenSpec
from sloeitem import SloeItem
from sloeoutputspec import SloeOutputSpec
from sloeplaylist import SloePlaylist
from sloeremoteitem import SloeRemoteItem
from sloetransferspec import SloeTransferSpec
from sloetreenode import SloeTreeNode

class SloeTree:
    instance = None

    def __init__(self):
        self.loaded = False
        self.reset()
        
        
    def reset(self):
        self.root_album = SloeAlbum()
        self.root_album.set_value("_location", "{root}")
        self.root_album.set_value("description", "")
        self.root_album.set_value("name", "{root}")
        self.root_album.set_value("title", "")
        self.root_album.set_value("uuid", "0226ed39-1ea6-487d-8c3a-dfbc71d8df4a")
        self.root_album.set_value("_is_root", True)

    
    @classmethod
    def inst(cls):
        if cls.instance is None:
            cls.instance = SloeTree()
        return cls.instance


    def get_root_album(self):
        return self.root_album


    def get_tree_uuid(self):
        return self.spec["uuid"]


    def find_in_tree(self, test_fn):
        def recurse(album, found):
            for item in album.items:
                if test_fn(item):
                    return item
            for album in album.albums:
                found = recurse(album, found)
                if found:
                    break
            return found
        return recurse(self.root_album, None)


    def get_item_from_spec(self, spec):
        def test(item):
            return (
                item.get("common_id", None) == spec.get("common_id", None) and
                item._subtree == spec["_subtree"] and
                item.name == spec["name"])
        return self.find_in_tree(test)


    def make(self):
        if not self.loaded:
            self.load()

    album_ini_regex = re.compile(r"(.*)-ALBUM=([0-9A-Fa-f-]{36}).ini$")
    genspec_ini_regex = re.compile(r"(.*)-GENSPEC=([0-9A-Fa-f-]{36})\.ini$")
    item_ini_regex = re.compile(r"(.*)-ITEM=([0-9A-Fa-f-]{36})\.ini$")
    outputspec_ini_regex = re.compile(r"(.*)-OUTPUTSPEC=([0-9A-Fa-f-]{36})\.ini$")
    playlist_ini_regex = re.compile(r"(.*)-PLAYLIST=([0-9A-Fa-f-]{36})\.ini$")
    remoteitem_ini_regex = re.compile(r"(.*)-REMOTEITEM=([0-9A-Fa-f-]{36})\.ini$")
    transferspec_ini_regex = re.compile(r"(.*)-TRANSFERSPEC=([0-9A-Fa-f-]{36})\.ini$")
        
    

    def load(self):
        logging.debug("Loading tree")
        treeroot = SloeConfig.get_global("treeroot")
        self.reset()
    
        ini_regex = re.compile(r".*\.ini$")
        sloe_ini_regex = re.compile(r"(.*)-([A-Z]+)=([0-9A-Fa-f-]{36})\.ini$")

        found_files = {}
        found_uuids = {}
        
        # First pass - collect list of filenames
        
        for walkroot, dirs, filenames in os.walk(treeroot):
            album_for_path = None
            for filename in filenames:
                full_path = os.path.join(walkroot, filename)
                ini_match = ini_regex.match(filename)
                if ini_match:
                    sloe_match = sloe_ini_regex.match(filename)
                    if not sloe_match:
                        logging.warning("Suspicious malformed(?) .ini file %s" % os.path.join(walkroot, filename))
                    else:   
                        name, obj_type, filename_uuid = sloe_match.group(1, 2, 3)
                        if obj_type not in found_files:
                            found_files[obj_type] = []
                        if filename_uuid in found_uuids:
                            raise SloeError("Duplicate UUIDs found in filenames: %s and %s" % (found_uuids[filename_uuid], full_path))
                        found_uuids[filename_uuid] = full_path
                            
                        found_files[obj_type].append((full_path, name, filename_uuid))
                    
                    
                    #bytecount += self.add_item_from_ini(primacy, worth, subdir_path, subtree, filename, name, filename_uuid, album_for_path)
                    #filecount += 1


        #logging.info("Loaded %d item (%d MB) records from %s" % (filecount, bytecount / 2**20, subdir_path))
        messages = []
        for k in sorted(found_files.keys()):
            messages.append("%s:%d" % (k, len(found_files[k])))
        logging.info("Found objects: %s" % ", ".join(messages))
        
        # Load albums first as they contain the other objects.  The directory walks insures that
        # parent albums will be processed before their subalbums


        albums_by_subtree = { "": self.root_album}
        
        def parent_from_path(obj_path):
            subtree = string.replace(os.path.relpath(dir_path, treeroot), "\\", "/")
            parent_subtree = os.path.dirname(subtree)
            parent_album = albums_by_subtree.get(parent_subtree, None)
            if parent_album is None:
                raise SloeError("Album has no parent in its parent directory: '%s'" % full_path)
            return parent_album

        for album_def in found_files["ALBUM"]:
            full_path, name, filename_uuid = album_def
            dir_path = os.path.dirname(full_path)
            parent_album = parent_from_path(full_path)
                    
            new_album = self.get_album_from_ini(full_path, filename_uuid)
            parent_album.add_child_obj(new_album)
            logging.debug("Added album %s to album %s" % (new_album.get("_subtree", "!")+":"+new_album.name,
                                                          parent_album.get("_subtree", "!")+":"+parent_album.name))
            subtree = string.replace(os.path.relpath(dir_path, treeroot), "\\", "/")
            albums_by_subtree[subtree] = new_album

        # Albums done so remove from found file list
        found_files["ALBUM"] = []
            
            
        # Load items - file check and count has special handling
        for item_def in found_files["ITEM"]:
            full_path, name, filename_uuid = item_def
            dest_album = parent_from_path(full_path)
            self.add_item_from_ini(full_path, filename_uuid, dest_album)

        # Items done so remove from found file list
        found_files["ITEM"] = []
        
        
        # Load other elements
        for obj_type in sorted(found_files.keys()):
            for obj_def in found_files[obj_type]:
                full_path, name, filename_uuid = album_def


    def get_album_from_ini(self, full_path, filename_uuid):
        
        album = SloeAlbum.new_from_ini_file(full_path, "SloeTree.add_album_from_ini: " + full_path)

        if album.uuid != filename_uuid: # Both are strings
            raise SloeError("filename/content uuid mismatch %s != %s in %s" %
                            (album.uuid, filename_uuid, full_path))

        return album


    @classmethod 
    def walk_albums(cls, album=None):
        if album is None:
            album = cls.inst().root_album
        yield album
        for subalbum in album.albums:
            for x in cls.walk_albums(subalbum):
                yield x


    @classmethod 
    def find_album_or_none(cls, album_uuid):
        for album in cls.walk_albums(cls.inst().root_album):
            if album.uuid == album_uuid:
                return album

        return None


    def add_item_from_ini(self, full_path, filename_uuid, dest_album):
        item = self.add_obj_from_ini("ITEM", full_path, filename_uuid, dest_album)

        filesize = 0
        target_path = os.path.join(os.path.dirname(full_path), item.leafname)
        filestat = os.stat(target_path)
        if os.path.stat.S_ISREG(filestat.st_mode):
            filesize = filestat.st_size
        else:
            logging.warning("Missing file %s" % target_path)

        return filesize


    def add_obj_from_ini(self, name, full_path, filename_uuid, dest_album):
        obj = SloeTreeNode.get_factory(name).new_from_ini_file(full_path, "SloeTree.add_obj_from_ini: " + full_path)
        if obj.uuid != filename_uuid: # Both are strings
            raise SloeError("filename/content uuid mismatch %s != %s in %s" %
                            (obj.uuid, filename_uuid, full_path))        
        dest_album.add_child_obj(obj)
        return obj
