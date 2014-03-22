
import logging
import os
import sys
from pprint import pprint, pformat

from sloeconfig import SloeConfig
from sloeerror import SloeError
from sloetreenode import SloeTreeNode


class SloeItem(SloeTreeNode):
    MANDATORY_ELEMENTS = ("leafname", "name")

    def __init__(self):
        SloeTreeNode.__init__(self, "item", "01")


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
            
        self.verify_creation_data()


    @classmethod
    def new_from_ini_file(cls, ini_filepath, error_info):
        item = SloeItem()
        item.create_from_ini_file(ini_filepath, error_info)
        return item


    def get_file_dir(self):
        root_dir = SloeConfig.inst().get_global("treeroot")
        return os.path.join(root_dir, self._d["_primacy"], self._d["_worth"], self._d["_subtree"])


    def get_file_path(self):
        return os.path.join(self.get_file_dir(), self._d["leafname"])
    

    def get_ini_filepath(self):
        treepath = os.path.dirname(self.get_file_path())
        return os.path.join(treepath, self.get_ini_leafname());


    def dump(self):
        return pformat(self._d)


    def __repr__(self):
        return "|Item|%s" % pformat(self._d)


    
SloeTreeNode.add_factory("ITEM", SloeItem)