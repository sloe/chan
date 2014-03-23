
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
        ret_items = []
        # Use simple parent album selector for now
        selector = self.get("selector", None)
        selector_genspec_name = self.get("selector_genspec_name", None)
        parent_album = SloeTreeNode.get_object_by_uuid(self._parent_album_uuid)
        for remoteitem in parent_album.remoteitems:
            extracted_remoteitem = SloeUtil.extract_common_id(remoteitem.common_id)
            add_item = True
            if selector is not None and not sloelib.SloeTreeUtil.object_matches_selector(remoteitem, params):
                logging.debug("Rejected item '%s' - does not match selector" % remoteitem.name)
                add_item = False
            else:
                item = SloeTreeNode.get_object_by_uuid(extracted_remoteitem["I"])
                extracted_item = SloeUtil.extract_common_id(item.common_id)
                if selector_genspec_name is not None:
                    genspec = SloeTreeNode.get_object_by_uuid(extracted_item["G"])
                    if selector_genspec_name != genspec.name:
                        logging.debug("Rejected item '%s' - selector_genspec_name(%s) != genspec.name(%s)" % (remoteitem.name, selector_genspec_name, genspec.name))
                        add_item = False
                        
            if add_item:
                logging.debug("Added item '%s'" % remoteitem.name)
                ret_items.append(remoteitem)
                
        return ret_items
        

    def __repr__(self):
        return "|SloePlaylist|%s" % pformat(self._d)


SloeTreeNode.add_factory("PLAYLIST", SloePlaylist)
