
import ConfigParser
import logging
import os
import sys
from pprint import pprint, pformat

from sloeerror import SloeError

class SloeTreeNode(object):
  MANDATORY_ELEMENTS = []

  def __init__(self, _type):
    self._type = _type
    self._d =  {
      "type": _type
    }


  def get(self, name, default):
    node = object.__getattribute__(self, "_d")
    if name in node:
      return node[name]
    else:
      return default


  def get_key(self):
      return "%s-%s" % (self._d["type"], str(self._d["uuid"]))


  def set_value(self, name, value):
    self._d[name] = value


  def __getattr__(self, name):
    node = object.__getattribute__(self, "_d")
    if name in node:
      return node[name]
    else:
      raise AttributeError(name)


  def create_from_ini_file(self, ini_filepath, error_info):
    with open(ini_filepath, "rb") as ini_fp:
      self.create_from_ini_fp(ini_fp, error_info)
      self._d["_location"] = os.path.dirname(ini_filepath)


  def create_from_ini_fp(self, ini_fp, error_info):
    self._d =  {
      "type": self._type
    }
    parser = ConfigParser.RawConfigParser()
    parser.readfp(ini_fp)
    file_data = {}
    for section in parser.sections():
      file_data[section] = {}
      for item_name, value in parser.items(section):
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1]
        file_data[section][item_name] = value
    _d = {}
    override = {}
    in_file_uuid = None
    try:
      for section, v in file_data.iteritems():
        if "uuid" in v:
          if in_file_uuid is not None:
            raise SloeError("Multiple uuid elements present")
          in_file_uuid = v["uuid"]
      section_with_uuid = "%s-%s" % (self._type, in_file_uuid or "NONE")

      for section, v in file_data.iteritems():
        if section == "override":
          override = v
        elif section == "auto" or section == self._type or section == section_with_uuid:
          _d.update(v)
        elif section.startswith(self._type):
          raise SloeError("in-file section/uuid mismatch %s != %s" %
            (section, section_with_uuid))
        else:
          raise SloeError("illegal section name %s" %
            section)
      _d.update(override)
      self.verify_file_data(_d)
    except SloeError, e:
      raise SloeError("%s (%s)" % (str(e), error_info))

    self._d.update(_d)


  def verify_file_data(self, file_data):
    missing_elements = []
    for element in self.MANDATORY_ELEMENTS:
      if element not in file_data:
        missing_elements.append(element)

    if len(missing_elements) > 0:
      raise SloeError("Missing elements %s in .ini file" % ", ".join(missing_elements))


  def get_ini_leafname(self):
    return "%s-%s=%s.ini" % (self._d["name"], self._d["type"].upper(), self._d["uuid"])


  def get_ini_filepath(self):
    return os.path.join(self._d["_save_dir"], self.get_ini_leafname());


  def save_to_file(self):
    parser = ConfigParser.ConfigParser()
    section = self.get_key()
    parser.add_section(section)
    for name, value in self._d.iteritems():
      if not name.startswith("_"):
        parser.set(section, name, '"%s"' % str(value))

    with open(self.get_ini_filepath(), "wb") as file:
      parser.write(file)
