
import logging
from pprint import pprint, pformat
import uuid

from sloeconfig import SloeConfig
from sloetreenode import SloeTreeNode

class SloeAlbum(SloeTreeNode):
    def __init__(self, name):
        SloeTreeNode.__init__(self, "album")
        self._d["name"] = name
        self._albums = {}
        self._items = {}


    def get_or_create_album(self, name):
        if name not in self._albums:
            self._albums[name] = SloeAlbum(name)
        return self._albums[name]


    def get_albums(self):
        return self._albums.values()

    def get_items(self):
        return self._items.values()


    def add_album(self, album):
        self._albums[album.name] = album


    def add_item(self, item):
        self._items[item.uuid] = item





