
import logging
from pprint import pprint, pformat
import re

from sloeconfig import SloeConfig
from sloeerror import SloeError
from sloetreenode import SloeTreeNode

class SloeAlbum(SloeTreeNode):
    MANDATORY_ELEMENTS = ("name", "uuid")
    CONTENT_TYPES = ("album", "genspec", "item", "order", "outputspec", "playlist", "remoteitem", "remoteplaylist", "transferspec")
    
    def __init__(self):
        SloeTreeNode.__init__(self, "album", "02")
        for content_name in self.CONTENT_TYPES:
            setattr(self, "%s_dict" % content_name, {})
            setattr(self, "%ss" % content_name, [])


    @classmethod
    def new_from_ini_file(cls, ini_filepath, error_info):
        album = SloeAlbum()
        album.create_from_ini_file(ini_filepath, error_info)
        return album


    def get_ini_leafname(self):
        return "+" + SloeTreeNode.get_ini_leafname(self)


    def create_new(self, name, full_path):
        # Stuff below needs moving into a plugin
        title = ""
        match = re.match(r'mays([0-9]{4})$', name)
        if match:
            title = "Cambridge May Bumps %s" % match.group(1)

        match = re.match(r'hoc([0-9]{4})$', name)
        if match:
            title = "Head of the Cam %s" % match.group(1)

        match = re.match(r'div(.*)$', name)
        if match:
            title = "Division %s" % match.group(1).upper()

        day_map = {
            "mon" : "Monday",
            "tues" : "Tuesday",
            "wed" : "Wednesday",
            "thurs" : "Thursday",
            "fri" : "Friday",
            "sat" : "Saturday",
            "sun" : "Sunday"
        }

        if name in day_map.keys():
            title = day_map[name]

        match = re.match(r'div(.*)$', name)
        if match:
            title = "%s" % match.group(1).upper()

        self._d.update({
            "name" : name,
            "_location" : full_path,
            "title" : title
        })
        self.create_uuid()
        self.verify_creation_data()
        self.add_to_library()


    def get_child_album_or_none(self, uuid):
        return self.album_dict.get(uuid, None)
    

    def add_child_obj(self, obj):
        obj_dict = getattr(self, "%s_dict" % obj.type, None)
        obj_store = getattr(self, "%ss" % obj.type, None)
        if obj_dict is None or obj_store is None:
            raise SloeError("Album cannot store content of type %s" % obj.type)

        obj_dict[obj.uuid] = obj
        obj_store.append(obj)
        obj.set_value("_parent_album_uuid", self._d["uuid"])
        return obj


    def sort_items(self):
        num_orders = len(self.orders)
        if num_orders != 1:
            logging.warning("Cannot sort album %s - no single order (%d present)" % (self.name, num_orders))
            return
        
        item_check = self.item_dict.copy()
        new_order = []
        for item_uuid in self.orders[0].get_item_order():
            if item_uuid not in item_check:
                logging.error("Iten %s in order but not in album" % item_uuid)
            else:
                del item_check[item_uuid]
                new_order.append(self.item_dict[item_uuid])
                
        num_remaining_items = len(item_check)
        if num_remaining_items > 5:
            logging.info("%d items in album but not in default order" % num_remaining_items)
        elif num_remaining_items > 0:
            logging.info("Items in album but not in default order: %s" % ", ".join(item_check.keys()))
        self.items = new_order
            
            
                
            
            
        

#    def __repr__(self):
#        return "|Album|ALBUMS=" + pformat(self.album_dict) + "\nITEMS=" + pformat(self.item_dict)


