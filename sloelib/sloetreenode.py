
import ConfigParser
import datetime
import logging
import os
from pprint import pprint, pformat
import sys
import uuid

from sloeconfig import SloeConfig
from sloeerror import SloeError

class SloeTreeNode(object):
    MANDATORY_ELEMENTS = {
        "type": "Type of the object",
        "uuid": "Primary ID of object"
    }
    OPTIONAL_ELEMENTS = {}
    FACTORIES = {}
    UUID_LIB = {}


    def __init__(self, _type, uuid_prefix = None):
        self._type = _type
        self._uuid_prefix = uuid_prefix
        self._d =  {
            "type": _type
        }


    def create_uuid(self):
        new_uuid = str(uuid.uuid4())
        if self._uuid_prefix is not None:
            new_uuid = self._uuid_prefix + new_uuid[len(self._uuid_prefix):]

        self._d["uuid"] = new_uuid


    def add_to_library(self):
        u = self._d.get("uuid", None)
        if u is None:
            raise SloeError("Cannot add item to library without UUID")
        if u in self.UUID_LIB:
            raise SloeError("Cannot add item '%s' to library - UUID already present" % u)
        SloeTreeNode.UUID_LIB[u] = self


    def get(self, name, default):
        node = object.__getattribute__(self, "_d")
        if name in node:
            return node[name]
        else:
            auto_name = "auto_"+name
            if auto_name in node:
                return node[auto_name]
            return default


    def get_key(self):
        return self._d["type"]


    def set_value(self, name, value):
        self._d[name] = value


    def set_values(self, **values):
        self._d.update(values)


    def __getattr__(self, name):
        node = object.__getattribute__(self, "_d")
        if name in node:
            return node[name]
        else:
            auto_name = "auto_"+name
            if auto_name in node:
                return node[auto_name]
            else:
                raise AttributeError("%s '%s' (%s) has no element named '%s' (%s)" % (
                    self._d.get("type", "<unknown>"),
                    self._d.get("name", "<unknown>"),
                    self._d.get("uuid", "no UUID"),
                    name,
                    self._d.get("_location", "no location")
                    ))


    def update(self, param_dict):
        self._d.update(param_dict)


    def create_from_ini_file(self, ini_filepath, error_info, add_to_library=True):
        with open(ini_filepath, "rb") as ini_fp:
            self.create_from_ini_fp(ini_fp, error_info, add_to_library)
        self.add_filepath_info(ini_filepath)


    def add_filepath_info(self, filepath):
        self._d["_location"] = os.path.dirname(filepath)
        rel_path = os.path.relpath(
            os.path.dirname(filepath),
            SloeConfig.get_global("treeroot"))
        rel_path = rel_path.replace("\\", "/")
        rel_split = rel_path.split("/")
        if len(rel_split) >= 1:
            self._d["_primacy"] = rel_split[0]
        if len(rel_split) >= 2:
            self._d["_worth"] = rel_split[1]
        if len(rel_split) >= 3:
            self._d["_subtree"] = "/".join(rel_split[2:])


    def get_full_subtree(self):
        treelist = []
        for elem in ("_primacy", "_worth", "_subtree"):
            if elem in self._d:
                treelist.append(self._d[elem])
        return "/".join(treelist)


    def create_from_ini_fp(self, ini_fp, error_info, add_to_library=True):
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
        new_d = self._d
        in_file_uuid = None
        try:
            for section, v in file_data.iteritems():
                if "uuid" in v:
                    if in_file_uuid is not None:
                        raise SloeError("Multiple uuid elements present")
                    in_file_uuid = v["uuid"]
            section_with_uuid = "%s-%s" % (self._type, in_file_uuid or "NONE")

            for section, v in file_data.iteritems():
                if section == self._type or section == section_with_uuid:
                    new_d.update(v)
                elif section.startswith(self._type):
                    raise SloeError("in-file section/uuid mismatch %s != %s" %
                                    (section, section_with_uuid))
                else:
                    raise SloeError("illegal section name %s" % section)

            self.verify_creation_data(new_d)
        except SloeError, e:
            raise SloeError("%s (%s)" % (str(e), error_info))

        for k, v in new_d.iteritems():
            content = v.replace("\\n", "\n")
            self._d[k] = content
        if add_to_library:
            self.add_to_library()


    def verify_confirm_missing(self, element):
        return True


    def verify_confirm_unknown(self, element):
        if element.startswith("_"):
            return False
        return True


    def verify_creation_data(self, creation_data=None):
        mandatory_elements = self.MANDATORY_ELEMENTS.keys()
        known_elements = set(self.MANDATORY_ELEMENTS.keys())
        known_elements.update(self.OPTIONAL_ELEMENTS.keys())
        for k in self.OPTIONAL_ELEMENTS.keys():
            known_elements.add("auto_"+k)

        if creation_data is None:
            creation_data = self._d

        missing_elements = []
        for element in mandatory_elements:
            if element not in creation_data and self.verify_confirm_missing(element):
                missing_elements.append(element)

        unknown_elements = []
        for element in creation_data:
            if element not in known_elements and self.verify_confirm_unknown(element):
                unknown_elements.append(element)

        failure_messages = []

        if len(missing_elements) > 0:
            failure_messages.append("Missing elements '%s' when creating object" % ", ".join(sorted(missing_elements)))

        if len(unknown_elements) > 0:
            failure_messages.append("Unknown elements '%s' when creating object" % ", ".join(sorted(unknown_elements)))

        if len(failure_messages) > 0:
            raise SloeError("\n".join(failure_messages))


    def get_ini_leafname(self):
        return "%s-%s=%s.ini" % (self._d["name"], self._d["type"].upper(), self._d["uuid"])


    def get_ini_filepath(self):
        return os.path.join(self._d["_location"], self.get_ini_leafname());


    def save_to_file(self):
        parser = ConfigParser.ConfigParser()
        section = self.get_key()
        parser.add_section(section)
        mandatory_set = self.MANDATORY_ELEMENTS.keys()
        mandatory = []
        automatic = []
        user = []

        for name in sorted(self._d.keys()):
            if name.startswith("_"):
                pass # Don't write to output
            elif name in mandatory_set:
                mandatory.append(name)
            elif name.startswith("auto_"):
                automatic.append(name)
            else:
                user.append(name)

        leading_keys = ['name', 'type', 'uuid']
        trailing_keys = [x for x in sorted(automatic + mandatory + user) if not x in leading_keys]
        for name in leading_keys + trailing_keys:
            if self._d[name] is not None:
                content = str(self._d[name]).replace("\n", "\\n")
                parser.set(section, name, '"%s"' % content)

        with open(self.get_ini_filepath(), "wb") as fp:
            fp.write("# Saved from object at %s\n\n" % datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%SZ'))
            parser.write(fp)


    def as_dict(self):
         # helper for web2py
        return self._d


    @classmethod
    def get_object_by_uuid(cls, u):
        obj = cls.UUID_LIB.get(u, None)
        if obj is None:
            raise SloeError("Cannot find object with UUID '%s'" % u)
        return obj


    @classmethod
    def get_object_by_uuid_or_none(cls, u):
        obj = cls.UUID_LIB.get(u, None)
        return obj


    @classmethod
    def add_factory(cls, tagname, classname):
        cls.FACTORIES[tagname] = classname


    @classmethod
    def get_factory(cls, tagname):
        if tagname not in cls.FACTORIES:
            raise SloeError("Unable to create object of type '%s' - no such type exists" % tagname)
        return cls.FACTORIES[tagname]