
import logging
import os
from pprint import pformat, pprint
import uuid

from sloealbum import SloeAlbum
from sloeconfig import SloeConfig
from sloeerror import SloeError
from sloeitem import SloeItem

class SloeOutputUtil(object):
  def __init__(self, tree):
    self.tree = tree
    glb_cfg = SloeConfig.get_global()
    self.verbose = glb_cfg.get_option("verbose")


  def _derive_outputdefs_recurse(self, indent, album):
    print "%s%sAlbum: %s '%s' (%s)" % (album.uuid, indent, album.name, album.title, album._location.replace("\\", "/"))
    for outputspec in album.get_outputspecs():
      pprint(outputspec)

    for album in album.get_albums():
      self._derive_outputdefs_recurse(indent+" ", album)


  def derive_outputdefs(self):
    root_album = self.tree.get_root_album()
    self._derive_outputdefs_recurse(" ", root_album)

