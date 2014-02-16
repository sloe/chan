
import glob
import json
import logging
import os
from pprint import pprint, pformat
import re
import string
import subprocess

import sloelib

class SloeGenerateCfg:
  def __init__(self, app):
    self.app = app
    self.glb_cfg = sloelib.SloeConfig.get_global()


  def enter(self, tree_names):
    for tree_name in tree_names:
      self.process_tree(tree_name)


  def process_tree(self, tree_name):
    if self.glb_cfg.get_option("final"):
      primacy = "final"
    else:
      primacy = "primary"

    for worth, walkroot in sloelib.SloeTrees.inst().get_treepaths(primacy, tree_name).iteritems():
      logging.debug("generate_cfg walking tree directory %s" % walkroot)

      if not os.path.exists(walkroot):
        os.makedirs(walkroot)
      self.process_dir(os.path.basename(walkroot), walkroot)

      for root, dirs, files in os.walk(walkroot, topdown=True, followlinks=False):
        for _dir in dirs:
          self.process_dir(os.path.basename(_dir), os.path.join(root, _dir))

      for root, dirs, files in os.walk(walkroot, topdown=True, followlinks=False):
        for file in files:
          match = re.match(r"^(.*)\.(flv|mp4|f4v)$", file)
          if match:
            spec = {
              "leafname" : file,
              "name" : match.group(1),
              "primacy" : primacy,
              "tree" : tree_name,
              "subtree" : string.replace(os.path.relpath(root, walkroot), "\\", "/"),
              "worth" : worth
            }
            self.process_file(spec)


  def process_dir(self, name, full_path):
    logging.debug("Processing directory %s" % full_path)
    album_files = glob.glob(os.path.join(full_path, "*ALBUM=*.ini"))
    if album_files == []:
      logging.debug("Creating template album file in %s" % full_path)
      album = sloelib.SloeAlbum()
      album.create_new(name, full_path)
      if not self.glb_cfg.get_option("dryrun"):
        album.save_to_file()


  def process_file(self, spec):
    logging.debug("Processing file with spec %s" % repr(spec))

    current_tree = sloelib.SloeTrees.inst().get_tree(spec["tree"])
    existing_item = current_tree.get_item_from_spec(spec)
    item = sloelib.SloeItem()
    item.create_new(existing_item, spec)
    self.detect_video_params(item)
    if not self.glb_cfg.get_option("dryrun"):
      item.save_to_file()


  def detect_video_params(self, item):
    command = [
      self.app.get_global("ffprobe"),
      item.get_file_path(),
      "-print_format", "json", "-show_format", "-show_streams"]

    p = subprocess.Popen(command, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    (json_out, stderr) = p.communicate()
    if p.returncode != 0:
      logging.error("ffprobe failed (rc=%d)\n%s" % (p.returncode, stderr))
      raise sloelib.SloeError("ffprobe failed (rc-%d)" % p.returncode)
    ffinfo = json.loads(json_out)
    for stream in ffinfo["streams"]:
      if stream["codec_type"] == "video":
        for name in ("codec_name", "width", "height", "pix_fmt", "level", "avg_frame_rate", "duration", "nb_frames"):
          if name in stream:
            item.set_value("video_" + name, stream[name])
      elif stream["codec_type"] == "audio":
        for name in ("codec_name", "sample_fmt", "sample_rate", "channels", "duration", "nb_frames"):
          if name in stream:
            item.set_value("audio_" + name, stream[name])
      else:
        handler_name = stream.get("tags", {}).get("handler_name", "")
        if handler_name == "Timed Metadata Handler":
          logging.debug("Ignoring Timed Metadata Handler stream")
        else:
          logging.error("Ignoring unknown stream %s" % pformat(stream))
    for name in ("format_name", "format_long_name", "size", "bit_rate"):
      if name in ffinfo["format"]:
        item.set_value("video_" + name, ffinfo["format"][name])
