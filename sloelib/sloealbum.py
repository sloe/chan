
import logging
from pprint import pprint, pformat
import re

from sloeconfig import SloeConfig
from sloeerror import SloeError
from sloetreenode import SloeTreeNode

class SloeAlbum(SloeTreeNode):
    MANDATORY_ELEMENTS = ("name", "uuid")
    def __init__(self):
        SloeTreeNode.__init__(self, "album", "02")
        self.subalbum_dict = {}
        self.genspec_dict = {}
        self.item_dict = {}
        self.outputspec_dict = {}
        self._album_names_to_uuids = {}


    @classmethod
    def new_from_ini_file(cls, ini_filepath, error_info):
        album = SloeAlbum()
        album.create_from_ini_file(ini_filepath, error_info)
        return album


    def get_ini_leafname(self):
        return "+" + SloeTreeNode.get_ini_leafname(self)


    def create_new(self, name, full_path):
        # Stuff below needs moving into a plugin
        title = ""
        match = re.match(r'mays([0-9]{4})$', name)
        if match:
            title = "Cambridge May Bumps %s" % match.group(1)

        match = re.match(r'hoc([0-9]{4})$', name)
        if match:
            title = "Head of the Cam %s" % match.group(1)

        match = re.match(r'div(.*)$', name)
        if match:
            title = "Division %s" % match.group(1).upper()

        day_map = {
            "mon" : "Monday",
            "tues" : "Tuesday",
            "wed" : "Wednesday",
            "thurs" : "Thursday",
            "fri" : "Friday",
            "sat" : "Saturday",
            "sun" : "Sunday"
        }

        if name in day_map.keys():
            title = day_map[name]

        match = re.match(r'div(.*)$', name)
        if match:
            title = "%s" % match.group(1).upper()

        self._d.update({
            "name" : name,
            "_location" : full_path,
            "title" : title
        })
        self.create_uuid()
        self.verify_creation_data()

    def get_child_album_by_name(self, name):
        uuid = self._album_names_to_uuids.get(name, None)
        if uuid is None:
            raise SloeError("Missing album '%s'" % name)
        return get_child_album(uuid)


    def get_child_album(self, uuid):
        album = self.subalbum_dict.get(uuid, None)
        if album is None:
            raise SloeError("Missing album '%s'" % name)
        return album


    def get_child_album_or_none(self, uuid):
        return self.subalbum_dict.get(uuid, None)


    @property
    def subalbums(self):
        return self.subalbum_dict.values()


    @property
    def genspecs(self):
        return self.genspec_dict.values()


    @property
    def items(self):
        return self.item_dict.values()


    @property
    def outputspecs(self):
        return self.outputspec_dict.values()


    def add_child_album(self, obj):
        obj.set_value("_parent_album_uuid", self.uuid)
        self.subalbum_dict[obj.uuid] = obj
        self._album_names_to_uuids[obj.name] = obj.uuid
        return obj


    def add_child_genspec(self, obj):
        self.genspec_dict[obj.uuid] = obj
        obj.set_value("_parent_album_uuid", self._d["uuid"])


    def add_child_item(self, obj):
        self.item_dict[obj.uuid] = obj
        obj.set_value("_parent_album_uuid", self._d["uuid"])


    def add_child_outputspec(self, obj):
        self.outputspec_dict[obj.uuid] = obj
        obj.set_value("_parent_album_uuid", self._d["uuid"])


    def __repr__(self):
        return "|Album|ALBUMS=" + pformat(self.subalbum_dict) + "\nITEMS=" + pformat(self.item_dict)


