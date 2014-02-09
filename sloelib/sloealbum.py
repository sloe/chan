
import logging
from pprint import pprint, pformat
import uuid

from sloeconfig import SloeConfig
from sloeerror import SloeError
from sloetreenode import SloeTreeNode

class SloeAlbum(SloeTreeNode):
  MANDATORY_ELEMENTS = ("name", "uuid")
  def __init__(self):
    SloeTreeNode.__init__(self, "album")
    self._albums = {}
    self._items = {}
    self._album_names_to_uuids = {}


  @classmethod
  def new_from_ini_file(cls, ini_filepath, error_info):
    album = SloeAlbum()
    album.create_from_ini_file(ini_filepath, error_info)
    return album


  def get_ini_leafname(self):
    return "+" + SloeTreeNode.get_ini_leafname(self)


  def create_new(self, name, full_path):
    self._d.update({
      "name" : name,
      "_save_dir" : full_path,
      "title" : "<Untitled>",
      "uuid" : uuid.uuid4()
    })


  def get_child_album_by_name(self, name):
    uuid = self._album_names_to_uuids.get(name, None)
    if uuid is None:
      raise SloeError("Missing album '%s'" % name)
    return get_child_album(uuid)


  def get_child_album(self, uuid):
    album = self._albums.get(uuid, None)
    if album is None:
      raise SloeError("Missing album '%s'" % name)
    return album


  def get_child_album_or_none(self, uuid):
    return self._albums.get(uuid, None)


  def get_albums(self):
    return self._albums.values()


  def get_items(self):
    return self._items.values()


  def add_child_album(self, album):
    album.set_value("parent_album", self.uuid)
    self._albums[album.uuid] = album
    self._album_names_to_uuids[album.name] = album.uuid
    return album


  def add_child_item(self, item):
    self._items[item.uuid] = item
    item.set_value("parent_album", self._d["uuid"])


  def __repr__(self):
    return "ALBUMS=" + pformat(self._albums) + "\nITEMS=" + pformat(self._items)



