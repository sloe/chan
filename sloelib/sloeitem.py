
from ConfigParser import ConfigParser
import logging
import os
import sys
from pprint import pprint, pformat
import uuid

from sloetrees import SloeTrees

class SloeItem:
  def __init__(self):
    self.data = {}


  def create_new(self, spec):

    current_tree = SloeTrees.inst().get_tree(spec["tree"])
    source = current_tree.get_item_from_spec(spec)

    if source:
      # Preserve UUID of item
      self.data["uuid"] = source["uuid"]
    else:
      # No pre-existing item, so take all info from passed-in spec
      source = spec
      self.data["uuid"] = uuid.uuid4()

    for element in ("leafname", "name", "primacy", "tree", "subtree", "worth"):
      if source[element] != spec[element]:
        logging.error("Mismatched original item: element %s new %s !=  old %s" % (
          element, spec[element], source[element]))
        print "%s %s" % (pformat(spec), pformat(source))
      self.data[element] = source[element]


  def get_file_dir(self):
    root_dir = SloeTrees.inst().get_tree_root_dir(self.data["tree"])
    return os.path.join(root_dir, self.data["primacy"], self.data["worth"], self.data["tree"], self.data["subtree"])


  def get_filepath(self):
    return os.path.join(self.get_file_dir(), self.data["leafname"])


  def get_key(self):
    return "item-%s" % str(self.data["uuid"])


  def get_ini_leafname(self):
    return "%s-%s.ini" % (self.data["name"], self.data["uuid"])


  def get_ini_filepath(self):
    treepath = os.path.dirname(self.get_filepath())
    return os.path.join(treepath, self.get_ini_leafname());


  def savetofile(self):
    parser = ConfigParser()
    section = self.get_key()
    parser.add_section(section)
    for name, value in self.data.iteritems():
      parser.set(section, name, '"%s"' % str(value))

    with open(self.get_ini_filepath(), "wb") as file:
      parser.write(file)


  def dump(self):
    return pformat(self.data)
