
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
        self.load_filesize = True
        self.reset()


    def reset(self):
        self.root_album = SloeAlbum()
        SloeTreeNode.UUID_LIB = {}
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


    def load(self):
        treeroot = SloeConfig.get_global("treeroot")
        logging.info("Loading tree from %s" % treeroot)
        self.reset()

        ini_regex = re.compile(r".*\.ini$")
        sloe_ini_regex = re.compile(r"(.*)-([A-Z]+)=([0-9A-Fa-f-]{36})\.ini$")

        found_files = {}
        found_uuids = {}
        order_files = []

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
                if filename == "order.txt":
                    order_files.append(full_path)


        messages = []
        for k in sorted(found_files.keys()):
            messages.append("%s:%d" % (k, len(found_files[k])))
        logging.info("Found objects: %s" % ", ".join(messages))

        # Load albums first as they contain the other objects.  The directory walks insures that
        # parent albums will be processed before their subalbums

        albums_by_subpath = { "": self.root_album}
        # Using treeroot_parent avoids problems where an empty subtree is represented as '.'
        treeroot_parent = os.path.dirname(treeroot)

        for album_def in found_files["ALBUM"]:
            full_path, name, filename_uuid = album_def
            dir_path = os.path.dirname(full_path)
            # For albums, the parent is the album in the directory above.  For other objects,
            # it's the album in the current directory
            subtree = string.replace(os.path.relpath(dir_path, treeroot_parent), "\\", "/")
            if subtree == ".":
                subtree = ""
            parent_subtree = os.path.dirname(subtree)
            if parent_subtree == ".":
                parent_subtree = ""
            parent_album = albums_by_subpath.get(parent_subtree, None)
            if parent_album is None:
                raise SloeError("Album has no parent in its parent directory: '%s'" % full_path)
            new_album = self.get_album_from_ini(full_path, filename_uuid)
            parent_album.add_child_obj(new_album)
            albums_by_subpath[subtree] = new_album

        # Albums done so remove from found file list
        found_files["ALBUM"] = []

        def parent_album_from_path(obj_path):
            subtree = string.replace(os.path.relpath(os.path.dirname(obj_path), treeroot_parent), "\\", "/")
            parent_album = albums_by_subpath.get(subtree, None)
            if parent_album is None:
                raise SloeError("Object has no parent in its parent directory: '%s'" % obj_path)
            return parent_album

        # Load items - file check and count has special handling
        byte_count = 0
        for item_def in found_files["ITEM"]:
            full_path, name, filename_uuid = item_def
            dest_album = parent_album_from_path(full_path)
            bytes_for_file = self.add_item_from_ini(full_path, filename_uuid, dest_album)
            if bytes_for_file is not None:
                byte_count += bytes_for_file


        # Items done so remove from found file list
        num_items = len(found_files["ITEM"])
        found_files["ITEM"] = []

        # Load other elements
        for obj_type in sorted(found_files.keys()):
            for obj_def in found_files[obj_type]:
                full_path, name, filename_uuid = obj_def
                dest_album = parent_album_from_path(full_path)
                self.add_obj_from_ini(obj_type, full_path, filename_uuid, dest_album)

        # Load order files.  These are plain text files
        for obj_path in order_files:
            dest_album = parent_album_from_path(obj_path)
            self.add_order_from_file(obj_path, dest_album)

        dest_album.sort_items()

        logging.info("Loaded tree (%d items, %.1fGB)" % (num_items, byte_count / 3**20))


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

        filesize = None
        if self.load_filesize:
            target_path = os.path.join(os.path.dirname(full_path), item.leafname)
            if not os.path.exists(target_path):
                logging.warning("Missing file %s" % target_path)
            else:
                filestat = os.stat(target_path)
                if os.path.stat.S_ISREG(filestat.st_mode):
                    filesize = filestat.st_size

        return filesize


    def add_obj_from_ini(self, obj_type, full_path, filename_uuid, dest_album):
        obj = SloeTreeNode.get_factory(obj_type).new_from_ini_file(full_path, "SloeTree.add_obj_from_ini: " + full_path)
        if obj.uuid != filename_uuid: # Both are strings
            raise SloeError("filename/content uuid mismatch %s != %s in %s" %
                            (obj.uuid, filename_uuid, full_path))
        dest_album.add_child_obj(obj)
        return obj


    def add_order_from_file(self, full_path, dest_album):
        obj = SloeTreeNode.get_factory("ORDER").new_from_order_file(full_path, dest_album, "SloeTree.add_order_from_file: " + full_path)
        dest_album.add_child_obj(obj)
        return obj
