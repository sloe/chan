
import logging
import os
from pprint import pformat, pprint
import uuid

from sloealbum import SloeAlbum
from sloeconfig import SloeConfig
from sloeerror import SloeError
from sloeitem import SloeItem

class SloeTreeUtil(object):
  def __init__(self, tree):
    self.tree = tree
    glb_cfg = SloeConfig.get_global()
    self.verbose = glb_cfg.get_option("verbose")


  def _ls_album_recurse(self, indent, album):
    try:
      print "%s%sAlbum: %s '%s' (%s)" % (album.uuid, indent, album.name, album.title, album._location.replace("\\", "/"))
      if self.verbose:
        pprint(album._d)
      for item in album.get_items():
        item_spec = ("%sx%s %sFPS %.2fs %.1fMB" %
           (item.video_width, item.video_height, item.video_avg_frame_rate, float(item.video_duration), float(item.video_size) / 2**20))
        print "%s%s %s (%s %s)" % (item.uuid, indent, item.name, os.path.splitext(item.leafname)[1], item_spec)
        if self.verbose:
          pprint(item._d)

      for obj in album.get_genspecs():
        print "%s%sGenSpec: %s" % (obj.uuid, indent, obj.name)
        if self.verbose:
          pprint(obj._d)
      
      for obj in album.get_outputspecs():
        print "%s%sOutputSpec: %s" % (obj.uuid, indent, obj.name)
        if self.verbose:
          pprint(obj._d)

    except Exception, e:
      logging.error("Missing attribute for %s" % album.name)
      raise e
    for album in album.get_albums():
      self._ls_album_recurse(indent+" ", album)


  def print_ls(self):
    root_album = self.tree.get_root_album()
    self._ls_album_recurse(" ", root_album)

