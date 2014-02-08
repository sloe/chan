
import os
from pprint import pprint, pformat

import ConfigParser
from sloeerror import SloeError

class SloeConfig:
  get_globalance = None

  def __init__(self):
    self.reset()
    self.opt = None


  @classmethod
  def get_global(cls):
    if cls.get_globalance is None:
      cls.get_globalance = SloeConfig()
    return cls.get_globalance


  def reset(self):
    defaults  = {}
    self.parser = ConfigParser.SafeConfigParser(defaults)
    self.data_valid = False


  def appendfile(self, filename):
    files = self.parser.read(filename)
    if not files:
      raise SloeError("Could not read config file %s" % filename)
    self.data_valid = False


  def remake_data(self):
    if not self.data_valid:
      self.data = {}
      for section in self.parser.sections():
        self.data[section] = {}
        for name, value in self.parser.items(section):
          if not name.startswith("_"):
            self.data[section][name] = value
      self.data_valid = True


  def get_section(self, section):
    if not self.data_valid:
      self.remake_data()
    if section not in self.data:
      raise SloeError("Configuration section %s not present" % section)
    return self.data[section]


  def get(self, section, name):
    return self.get_section(section)[name]


  def set_options(self, opt):
    self.options = opt


  def get_option(self, name):
    return getattr(self.options, name)


  def dump(self):
    message = ""
    for section in ["DEFAULT"] + self.parser.sections():
      message += "[%s]\n" % section
      for name, value in self.parser.items(section):
        if not name.startswith("_"):
          message += "%s=%s\n" % (name, value)

    self.remake_data()
    message += pformat(self.data)
    return message
