
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


  @classmethod
  def new_from_ini_file(cls, ini_filepath, error_info):
    album = SloeAlbum()
    album.create_from_ini_file(ini_filepath, error_info)
    return album


  def get_album(self, name):
    album = self._albums.get(name, None)
    if album is None:
      raise SloeError("Missing album '%s'" % name)
    return album


  def get_album_or_none(self, name):
    return self._albums.get(name, None)


  def get_albums(self):
    return self._albums.values()


  def get_items(self):
    return self._items.values()


  def add_album(self, album):
    self._albums[album.name] = album


  def add_item(self, item):
    self._items[item.uuid] = item


  def create_album(self, path, name):
    pass



  def __repr__(self):
    return "ALBUMS=" + pformat(self._albums) + "\nITEMS=" + pformat(self._items)



