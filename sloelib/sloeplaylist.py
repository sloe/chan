
from collections import defaultdict
import logging
from pprint import pprint, pformat

from sloeconfig import SloeConfig
from sloeerror import SloeError
from sloetreenode import SloeTreeNode
from sloeutil import SloeUtil

class SloePlaylist(SloeTreeNode):
    MANDATORY_ELEMENTS = ("name", "priority", "uuid")
    def __init__(self):
        SloeTreeNode.__init__(self, "playlist", "09")


    @classmethod
    def new_from_ini_file(cls, ini_filepath, error_info):
        obj = SloePlaylist()
        obj.create_from_ini_file(ini_filepath, error_info)
        obj.priority = float(obj.priority)
        return obj


    def get_ordered_items(self):
        parent_album = SloeTreeNode.get_object_by_uuid(self._parent_album_uuid)
        if len(parent_album.orders) > 0:   
            order = parent_album.orders[0]
        else:
            source_album = SloeTreeNode.get_object_by_uuid(parent_album.source_album_uuid)
            if len(source_album.orders) > 0:    
                order = source_album.orders[0]
            else:
                logging.error("Cannot get order for album %s" % parent_album.name)
                
        item_uuid_to_order_map = order.get_item_uuid_to_order_map()
        prioritised_items = defaultdict(list)
        # Use simple parent album selector for now
        selector = self.get("selector", None)
        selector_genspec_name = self.get("selector_genspec_name", None)
        for i, remoteitem in enumerate(parent_album.remoteitems):
            priority = 0.0
            extracted_remoteitem = SloeUtil.extract_common_id(remoteitem.common_id)
            add_item = True
            if selector is not None and not sloelib.SloeTreeUtil.object_matches_selector(remoteitem, params):
                # logging.debug("Rejected item '%s' - does not match selector" % remoteitem.name)
                add_item = False
            else:
                final_item = SloeTreeNode.get_object_by_uuid(extracted_remoteitem["I"])
                extracted_final = SloeUtil.extract_common_id(final_item.common_id)
                item = SloeTreeNode.get_object_by_uuid(extracted_final["I"])                
                priority = 10000.0 * item_uuid_to_order_map[item.uuid]
                genspec = SloeTreeNode.get_object_by_uuid(extracted_final["G"])
                priority += genspec.priority
                if selector_genspec_name is not None and selector_genspec_name != genspec.name:
                    # logging.debug("Rejected item '%s' - selector_genspec_name(%s) != genspec.name(%s)" % (remoteitem.name, selector_genspec_name, genspec.name))
                    add_item = False

                        
            if add_item:
                prioritised_items[priority].append(remoteitem)
        
        ret_items = []
        for k in sorted(prioritised_items.keys()):
            ret_items += prioritised_items[k]
                
        return ret_items
        

    def __repr__(self):
        return "|SloePlaylist|%s" % pformat(self._d)


SloeTreeNode.add_factory("PLAYLIST", SloePlaylist)
