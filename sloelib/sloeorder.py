
import codecs
import logging
from pprint import pprint, pformat

from sloeconfig import SloeConfig
from sloeerror import SloeError
from sloetreenode import SloeTreeNode
from sloeutil import SloeUtil

class SloeOrder(SloeTreeNode):
    MANDATORY_ELEMENTS = ("name", "uuid")
    def __init__(self):
        SloeTreeNode.__init__(self, "order", "0a")

    @classmethod
    def new_from_ini_file(cls, ini_filepath, error_info):
        obj = SloeOrder()
        obj.create_from_ini_file(ini_filepath, error_info)
        return obj


    @classmethod
    def new_from_order_file(cls, full_path, parent_album, error_info):
        obj = SloeOrder()
        ordered_item_uuids = []
        for leafname in SloeUtil.get_unicode_file_lines(full_path):
            item_found = None
            leafname = leafname.rstrip()
            if not leafname.startswith('#') and leafname != "":
                for item in parent_album.items:
                    if item.leafname == leafname:
                        item_found = item
                        break
                    
                if not item_found:
                    raise SloeError("Item '%s' from '%s'cannot be found" % (leafname, full_path))
                ordered_item_uuids.append(item.uuid)
            
        for i, item_uuid in enumerate(ordered_item_uuids):
            obj._d["order%.1f" % (1.0 * (i+1))] = item_uuid
              
        obj.create_uuid()
        obj.add_filepath_info(full_path)
        obj.set_value("name", "order-%s" % str(obj.uuid))
        obj.verify_creation_data()
        return obj


    def get_item_order(self):
        order_value_to_uuid = {}
        for k in self._d.keys():
            if k.startswith("order"):
                val = float(k[5:])
                if val in order_value_to_uuid:
                    order_value_to_uuid[val].append(self._d[k])
                else:
                    order_value_to_uuid[val] = [self._d[k]]
                    
        ret_list = []
        for k in sorted(order_value_to_uuid.keys()):
            ret_list += order_value_to_uuid[k]
            
        return ret_list
                

    def get_item_uuid_to_order_map(self):
        item_order = self.get_item_order()
        ret_map = {}
        for i, u in enumerate(item_order):
            ret_map[u] = i
        
        return ret_map


    def __repr__(self):
        return "|Order|%s" % pformat(self._d)


    
SloeTreeNode.add_factory("ORDER", SloeOrder)
    