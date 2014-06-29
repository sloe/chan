
import os
from pprint import pprint, pformat

from sloeerror import SloeError

class SloeConfig(object):
    instance = None

    def __init__(self):
        self.sections = {}
        self.options = None

    @classmethod
    def inst(cls):
        if cls.instance is None:
            cls.instance = SloeConfig()
        return cls.instance


    @classmethod
    def get_option(cls, name):
        return cls.inst()._get_option(name)


    @classmethod
    def get_global(cls, name):
        return cls.inst().get_value("global", name)


    def get_section(self, section):
        if section not in self.sections:
            raise SloeError("Configuration section %s not present" % section)
        return self.sections[section]


    def get_value(self, section, name):
        return self.get_section(section)[name]


    def get_or_none(self, section, name):
        return self.get_section(section).get(name, None)


    def set_value(self, section, name, value):
        if section not in self.sections:
            self.sections[section] = {}
        self.sections[section][name] = value


    def set_options(self, opt):
        self.options = opt


    def _get_option(self, name):
        return getattr(self.options, name)


    def dump(self):
        message = ""
        for section_name, section in self.sections.iteritems():
            message += "[%s]\n" % section_name
            for name, value in section.iteritems():
                message += "%s=%s\n" % (name, value)

        return message
