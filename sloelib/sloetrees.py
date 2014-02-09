
import logging
import os
from pprint import pprint

from sloeconfig import SloeConfig
from sloetree import SloeTree

class SloeTrees:
  instance = None

  def __init__(self):
    self.trees = {}
    self.tree_uuids = {}


  @classmethod
  def inst(cls):
    if cls.instance is None:
      cls.instance = SloeTrees()
    return cls.instance


  def get_treepaths(self, primacy, tree_name):

    glb_cfg = SloeConfig.get_global()
    primacies = glb_cfg.get("global", "primacies").split(",")
    if primacy not in primacies:
      raise sloelib.SloeError("Invalid primacy %s" % primacy)
    root_dir = glb_cfg.get_tree_root_dir(tree_name)
    name = glb_cfg.get(glb_cfg.get_tree_key(tree_name), "name")

    retval = {}

    for worth in glb_cfg.get("global", "worths").split(","):
      retval[worth] = os.path.join(root_dir, primacy, worth, name)
    return retval


  def get_tree(self, tree_name):
    tree_uuid = self.tree_uuids.get(tree_name, None) or self._load_tree(tree_name)
    return self.trees[tree_uuid]


  def _create_tree(self, tree_name):
    logging.debug("Creating tree object for %s" % tree_name)

    glb_cfg = SloeConfig.get_global()
    tree_spec = glb_cfg.get_section(glb_cfg.get_tree_key(tree_name))
    tree_spec["name"] = tree_name
    new_tree = SloeTree(tree_spec)
    self.trees[tree_spec["uuid"]] = new_tree
    self.tree_uuids[tree_spec["name"]] = tree_spec["uuid"]
    return new_tree


  def _load_tree(self, tree_name):
    created_tree = self._create_tree(tree_name)
    created_tree.make()
    return created_tree.get_tree_uuid()

