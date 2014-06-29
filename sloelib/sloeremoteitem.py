
import logging
import os
from pprint import pprint, pformat

from sloeconfig import SloeConfig
from sloeerror import SloeError
from sloetreenode import SloeTreeNode


class SloeRemoteItem(SloeTreeNode):
    MANDATORY_ELEMENTS = {
        "common_id": "IDs of related items in common ID format",
        "name": "Primary name of the item",
        "remote_id": "Item identifier on remote system",
        "remote_url": "URL for remote item"
    }
    MANDATORY_ELEMENTS.update(SloeTreeNode.MANDATORY_ELEMENTS)
    OPTIONAL_ELEMENTS = {
        "description": "Description of item on remote system",
        "title": "Title of item on remote system"
    }
    OPTIONAL_ELEMENTS.update(SloeTreeNode.OPTIONAL_ELEMENTS)


    def __init__(self):
        SloeTreeNode.__init__(self, "remoteitem", "08")


    def create_new(self, existing_item, spec):
        if existing_item:
            # Preserve information in existing item
            for k, v in existing_item._d.iteritems():
                if not k.startswith("auto_"):
                    if k in spec and v != spec[k]:
                        logging.warn("Mismatched original item: element %s new %s !=  old %s" % (
                            k, v, spec[k]))

                    self._d[k] = v
            self._d.update(spec)

        else:
            self._d.update(spec)
            if "uuid" not in self._d:
                self.create_uuid()


    @classmethod
    def new_from_ini_file(cls, ini_filepath, error_info):
        item = SloeRemoteItem()
        item.create_from_ini_file(ini_filepath, error_info)
        return item


    def get_file_dir(self):
        root_dir = SloeConfig.inst().get_global("treeroot")
        return os.path.join(root_dir, self._d["_primacy"], self._d["_worth"], self._d["_subtree"])


    def get_ini_filepath(self):
        return os.path.join(self.get_file_dir(), self.get_ini_leafname());


    def __repr__(self):
        return "|RemoteItem|%s" % pformat(self._d)



SloeTreeNode.add_factory("REMOTEITEM", SloeRemoteItem)
