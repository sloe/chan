
import ConfigParser
import logging
import os
import sys
from pprint import pprint, pformat
import uuid

from sloeconfig import SloeConfig
from sloeerror import SloeError
from sloetreenode import SloeTreeNode


class SloeItem(SloeTreeNode):
  MANDATORY_ELEMENTS = ("leafname", "name", "primacy", "tree", "subtree", "worth")

  def __init__(self):
      SloeTreeNode.__init__(self, "item")


  def create_new(self, existing_item, spec):
      if existing_item:
          # Preserve UUID of item
          self._d["uuid"] = existing_item._d["uuid"]
      else:
          # No pre-existing item, so create new UUID
          self._d["uuid"] = uuid.uuid4()

      for element in self.MANDATORY_ELEMENTS:
          if existing_item is not None and existing_item._d[element] != spec[element]:
              logging.error("Mismatched original item: element %s new %s !=  old %s" % (
                  element, spec[element], existing_item[element]))
          self._d[element] = spec[element]


  def create_from_ini_file(self, ini_filepath, error_info):
      with open(ini_filepath, "rb") as ini_fp:
          self._create_from_ini_fp(ini_fp, error_info)


  @classmethod
  def new_from_ini_file(cls, ini_filepath, error_info):
      item = SloeItem()
      item.create_from_ini_file(ini_filepath, error_info)
      return item


  def _create_from_ini_fp(self, ini_fp, error_info):
      self._d = {}
      parser = ConfigParser.RawConfigParser()
      parser.readfp(ini_fp)
      file_data = {}
      for section in parser.sections():
          file_data[section] = {}
          for item_name, value in parser.items(section):
              if value.startswith('"') and value.endswith('"'):
                  value = value[1:-1]
              file_data[section][item_name] = value


      # Verification
      if len(file_data.keys()) != 1:
          raise SloeError("Only one section supported in .ini: %s" % error_info)

      for section, section__d in file_data.iteritems():
          _d = file_data[file_data.keys()[0]]
          if section != "item" and section != "item-%s" % _d["uuid"]:
              raise SloeError("in-file section/uuid mismatch %s != %s in %s" %
                  (section, "item-%s" % _d["uuid"], full_path))

      missing_elements = []
      for element in self.MANDATORY_ELEMENTS:
          if element not in _d:
              missing_elements.append(element)

      if len(missing_elements) > 0:
          raise SloeError("Missing elements %s in .ini: %s" % (", ".join(missing_elements), error_info))

      self._d = _d


  def get_file_dir(self):
      root_dir = SloeConfig.get_global().get_tree_root_dir(self._d["tree"])
      return os.path.join(root_dir, self._d["primacy"], self._d["worth"], self._d["tree"], self._d["subtree"])


  def get_filepath(self):
      return os.path.join(self.get_file_dir(), self._d["leafname"])

  def get_ini_filepath(self):
    treepath = os.path.dirname(self.get_filepath())
    return os.path.join(treepath, self.get_ini_leafname());


  def dump(self):
    return pformat(self._d)


  def __repr__(self):
    return pformat(self._d)

