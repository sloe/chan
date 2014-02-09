
import logging
import os
import re
from pprint import pformat, pprint
import string
import uuid

from sloealbum import SloeAlbum
from sloeconfig import SloeConfig
from sloeerror import SloeError
from sloeitem import SloeItem

class SloeTree:
  album_ini_regex = re.compile(r"(.*)-ALBUM=([0-9A-Fa-f-]{36}).ini$")
  item_ini_regex = re.compile(r"(.*)-ITEM=([0-9A-Fa-f-]{36})\.ini$")
  ini_regex = re.compile(r".*\.ini$")

  def __init__(self, spec):
      self.spec = spec
      self.loaded = False
      self.treedata = SloeAlbum()
      self.treedata.set_value("name", "root")
      self.treedata.set_value("uuid", "1a26ed39-1ea6-487d-8c3a-dfbc71d8df4a")


  def get_tree_uuid(self):
      return self.spec["uuid"]


  def find_in_tree(self, test_fn):
      def recurse(album, found):
          for item in album.get_items():
              if test_fn(item):
                  return item
          for album in album.get_albums():
              found = recurse(album, found)
              if found:
                  break
          return found
      return recurse(self.treedata, None)


  def get_item_from_spec(self, spec):
      def test(item):
          return (
              item.primacy == spec["primacy"] and
              item.subtree == spec["subtree"] and
              item.name == spec["name"])
      return self.find_in_tree(test)


  def make(self):
      if not self.loaded:
          self.load()


  def load(self):
    logging.debug("Loading tree %s" % self.spec["name"])
    glb_cfg = SloeConfig.get_global()

    for primacy in glb_cfg.get("global", "primacies").split(","):
      for worth in glb_cfg.get("global", "worths").split(","):
        subdir_path = os.path.join(self.spec["root_dir"], primacy, worth, self.spec["name"])
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
            elif self.ini_regex.match(filename) and not self.album_ini_regex.match(filename):
              logging.warning("Suspicious misnamed(?) .ini file %s" % os.path.join(root, filename))
        logging.info("Loaded %d item (%d MB) records from %s" % (filecount, bytecount / 2**20, subdir_path))


  def load_album_for_path(self, full_path):
    root_dir = self.spec["root_dir"]
    subtree = os.path.relpath(full_path, root_dir)
    album_dirs = [""]
    for _dir in subtree.replace("\\", "/").split("/"):
      album_dirs.append(os.path.join(album_dirs[-1], _dir))

    parent_album = self.treedata
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
        raise SloeError("Missing ALBUM= .ini files in %s" % full_path)

      parent_album = album_found
    return album_found


  def get_album_from_ini(self, subdir_path, subtree, filename, name, filename_uuid, parent_album):
    full_path = os.path.join(subdir_path, subtree, filename)
    album = SloeAlbum.new_from_ini_file(full_path, "SloeTree.add_album_from_ini: " + full_path)

    if album.uuid != filename_uuid: # Both are strings
      raise SloeError("filename/content uuid mismatch %s != %s in %s" %
        (item.uuid, filename_uuid, full_path))

    return album


  def add_item_from_ini(self, primacy, worth, subdir_path, subtree, filename, name, filename_uuid, dest_album):
    full_path = os.path.join(subdir_path, subtree, filename)
    item = SloeItem.new_from_ini_file(full_path, "SloeTree.add_item_from_ini: " + full_path)

    # Verification
    if primacy != item.get("primacy", ""):
      raise SloeError("primacy mismatch %s != %s in %s" %
        (primacy, item.get("primacy", "(missing)"), full_path))
    # Don't verify worth - can be changed by moving files
    if subtree != item.subtree:
      raise SloeError("subtree mismatch %s != %s in %s" %
        (subtree, item.subtree, full_path))

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

    id_uuid = uuid.UUID(item.uuid)
    dest_album.add_child_item(item)
    return filesize

  def __repr__(self):
      return ("SloeTree.spec=" + pformat(self.spec) +
          "\nSloeTree.loaded=" + pformat(self.loaded) +
          "\nSloeTree.treedata=" + pformat(self.treedata))
