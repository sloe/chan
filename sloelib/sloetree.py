
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
from sloeremoteitem import SloeRemoteItem
from sloetransferspec import SloeTransferSpec

class SloeTree:
    instance = None

    album_ini_regex = re.compile(r"(.*)-ALBUM=([0-9A-Fa-f-]{36}).ini$")
    genspec_ini_regex = re.compile(r"(.*)-GENSPEC=([0-9A-Fa-f-]{36})\.ini$")
    item_ini_regex = re.compile(r"(.*)-ITEM=([0-9A-Fa-f-]{36})\.ini$")
    outputspec_ini_regex = re.compile(r"(.*)-OUTPUTSPEC=([0-9A-Fa-f-]{36})\.ini$")
    remoteitem_ini_regex = re.compile(r"(.*)-REMOTEITEM=([0-9A-Fa-f-]{36})\.ini$")
    transferspec_ini_regex = re.compile(r"(.*)-TRANSFERSPEC=([0-9A-Fa-f-]{36})\.ini$")
    ini_regex = re.compile(r".*\.ini$")

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
            for album in album.subalbums:
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


    def load(self):
        logging.debug("Loading tree")
        self.reset()
        for primacy in SloeConfig.get_global("primacies").split(","):
            for worth in SloeConfig.get_global("worths").split(","):
                subdir_path = os.path.join(SloeConfig.get_global("treeroot"), primacy, worth)
                logging.debug("Walking path %s" % subdir_path)
                filecount = 0
                bytecount = 0

                for root, dirs, filenames in os.walk(subdir_path):
                    album_for_path = None
                    for filename in filenames:
                        match = self.item_ini_regex.match(filename)
                        if match:
                            name = match.group(1)
                            filename_uuid = match.group(2)
                            subtree = string.replace(os.path.relpath(root, subdir_path), "\\", "/")
                            
                            if album_for_path is None:
                                album_for_path = self.load_album_for_path(root)
                            bytecount += self.add_item_from_ini(primacy, worth, subdir_path, subtree, filename, name, filename_uuid, album_for_path)
                            filecount += 1
                        elif (self.ini_regex.match(filename) and not self.album_ini_regex.match(filename) and not
                              self.outputspec_ini_regex.match(filename) and not self.transferspec_ini_regex.match(filename)):
                            logging.warning("Suspicious misnamed(?) .ini file %s" % os.path.join(root, filename))
                logging.info("Loaded %d item (%d MB) records from %s" % (filecount, bytecount / 2**20, subdir_path))


    def load_album_for_path(self, full_path):
        root_dir = SloeConfig.get_global("treeroot")
        subtree = os.path.relpath(full_path, root_dir)
        album_dirs = [""]
        for _dir in subtree.replace("\\", "/").split("/"):
            album_dirs.append(os.path.join(album_dirs[-1], _dir))

        parent_album = self.root_album
        album_found = None
        for album_dir in album_dirs:
            album_found = None
            full_path = os.path.join(root_dir, album_dir)
            (_, _, filenames) = next(os.walk(full_path))
            for filename in filenames:
                match = self.album_ini_regex.match(filename)
                if match:
                    if album_found:
                        raise SloeError("Multiple ALBUM= .ini files in %s" % full_path)
                    name = match.group(1)
                    filename_uuid = match.group(2)
                    subtree = album_dir.replace("\\", "/")
                    album_from_ini = self.get_album_from_ini(album_dir, subtree, os.path.join(full_path, filename), name, filename_uuid, parent_album)
                    album_found = parent_album.get_child_album_or_none(album_from_ini.uuid)
                    if album_found is None:
                        album_found = parent_album.add_child_album(album_from_ini)

            if not album_found:
                logging.error("Missing ALBUM= .ini files in %s" % full_path)

            for filename in filenames:
                match = self.genspec_ini_regex.match(filename)
                if match:
                    name = match.group(1)
                    filename_uuid = match.group(2)
                    self.add_genspec_from_ini(os.path.join(full_path, filename), name, filename_uuid, album_found)
                match = self.outputspec_ini_regex.match(filename)
                
                if match:
                    name = match.group(1)
                    filename_uuid = match.group(2)
                    self.add_outputspec_from_ini(os.path.join(full_path, filename), name, filename_uuid, album_found)   
                match = self.remoteitem_ini_regex.match(filename)
                
                if match:
                    name = match.group(1)
                    filename_uuid = match.group(2)
                    self.add_remoteitem_from_ini(os.path.join(full_path, filename), name, filename_uuid, album_found)
                match = self.transferspec_ini_regex.match(filename)
                
                if match:
                    name = match.group(1)
                    filename_uuid = match.group(2)
                    self.add_transferspec_from_ini(os.path.join(full_path, filename), name, filename_uuid, album_found)                       

            parent_album = album_found
        return album_found


    def get_album_from_ini(self, subdir_path, subtree, filename, name, filename_uuid, parent_album):
        full_path = os.path.join(subdir_path, subtree, filename)
        album = SloeAlbum.new_from_ini_file(full_path, "SloeTree.add_album_from_ini: " + full_path)

        if album.uuid != filename_uuid: # Both are strings
            raise SloeError("filename/content uuid mismatch %s != %s in %s" %
                            (item.uuid, filename_uuid, full_path))

        return album


    @classmethod 
    def walk_albums(cls, album=None):
        if album is None:
            album = cls.inst().root_album
        yield album
        for subalbum in album.subalbums:
            for x in cls.walk_albums(subalbum):
                yield x


    @classmethod 
    def find_album_or_none(cls, album_uuid):
        for album in cls.walk_albums(cls.inst().root_album):
            if album.uuid == album_uuid:
                return album

        return None


    def add_item_from_ini(self, primacy, worth, subdir_path, subtree, filename, name, filename_uuid, dest_album):
        full_path = os.path.join(subdir_path, subtree, filename)
        item = SloeItem.new_from_ini_file(full_path, "SloeTree.add_item_from_ini: " + full_path)

        if item.uuid != filename_uuid: # Both are strings
            raise SloeError("filename/content uuid mismatch %s != %s in %s" %
                            (item.uuid, filename_uuid, full_path))

        filesize = 0
        target_path = os.path.join(subdir_path, subtree, item.leafname)
        filestat = os.stat(target_path)
        if os.path.stat.S_ISREG(filestat.st_mode):
            filesize = filestat.st_size
        else:
            logging.warning("Missing file %s" % target_path)

                
            
        if dest_album is not None:
            dest_album.add_child_item(item)
        return filesize


    def add_genspec_from_ini(self, full_path, name, filename_uuid, dest_album):
        item = SloeGenSpec.new_from_ini_file(full_path, "SloeTree.add_genspec_from_ini: " + full_path)
        dest_album.add_child_genspec(item)


    def add_outputspec_from_ini(self, full_path, name, filename_uuid, dest_album):
        item = SloeOutputSpec.new_from_ini_file(full_path, "SloeTree.add_outputspec_from_ini: " + full_path)
        dest_album.add_child_outputspec(item)


    def add_remoteitem_from_ini(self, full_path, name, filename_uuid, dest_album):
        item = SloeRemoteItem.new_from_ini_file(full_path, "SloeTree.add_remoteitem_from_ini: " + full_path)
        dest_album.add_child_remoteitem(item)
        

    def add_transferspec_from_ini(self, full_path, name, filename_uuid, dest_album):
        item = SloeTransferSpec.new_from_ini_file(full_path, "SloeTree.add_transferspec_from_ini: " + full_path)
        dest_album.add_child_transferspec(item)


    def __repr__(self):
        return ("|Tree|loaded=" + pformat(self.loaded) +
                "\ntreedata=" + pformat(self.root_album))