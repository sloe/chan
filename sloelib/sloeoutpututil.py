
import logging
import os
from pprint import pformat, pprint
import re
import uuid

from sloealbum import SloeAlbum
from sloeconfig import SloeConfig
from sloeerror import SloeError
from sloeitem import SloeItem
from sloeremoteitem import SloeRemoteItem
from sloeremoteplaylist import SloeRemotePlaylist
from sloetree import SloeTree
from sloetreeutil import SloeTreeUtil
from sloeutil import SloeUtil
from sloevarutil import SloeVarUtil
from sloevideoutil import SloeVideoUtil

class SloeOutputUtil(object):
    def __init__(self, tree):
        self.tree = tree
        glb_cfg = SloeConfig.inst()
        self.verbose = sloelib.SloeConfig.get_option("verbose")


    def _derive_outputdefs_recurse(self, indent, album):
        print "%sAlbum: %s '%s' (%s)" % (album.uuid, album.name, album.title, album._location.replace("\\", "/"))
        for outputspec in album.get_outputspecs():
            pprint(outputspec)

        for album in album.albums:
            self._derive_outputdefs_recurse(indent+" ", album)


    def derive_outputdefs(self):
        root_album = self.tree.get_root_album()
        self._derive_outputdefs_recurse(" ", root_album)


    @classmethod
    def get_output_subpath(cls, genspec, item, outputspec):
        output_path = outputspec.output_path

        replacements = {
            "basename" : os.path.splitext(os.path.basename(item.leafname))[0],
            "ext" : genspec.output_extension,
            "suffix" : genspec.output_suffix,
            "name" : item.name,
            "subtree" : item._subtree,
            }
        

        return SloeUtil.substitute_vars(output_path, replacements)
    
                
    @classmethod
    def get_output_path(cls, genspec, item, outputspec):  
        output_path = cls.get_output_subpath(genspec, item, outputspec)
        if not re.match(r'[\\/]', output_path) and not re.match(r'[A-Z]:[\\/]', output_path):
            output_path = os.path.join(SloeConfig.get_global("treeroot"), output_path)
            
        return output_path
    
    
    @classmethod
    def create_output_ini(cls, genspec, item, outputspec):
        current_tree = SloeTree.inst()
        output_subpath = cls.get_output_subpath(genspec, item, outputspec)
        dest_treelist = output_subpath.split("/")[:-1]
        parent_album = SloeTreeUtil.find_or_create_derived_album(item._parent_album_uuid, dest_treelist)
        
        common_id = "G=%s,I=%s,O=%s" % (genspec.uuid, item.uuid, outputspec.uuid)
        spec = {
            "_primacy" : dest_treelist[0],
            "_worth" : dest_treelist[1],
            "_subtree" : "/".join(dest_treelist[2:]),
                                    
            "common_id" : common_id,
            "leafname" : os.path.basename(output_subpath),
            "name" : item.name,
        }
        existing_item = current_tree.get_item_from_spec(spec)
        logging.info("existing item=%s"% pformat(existing_item))
        new_item = SloeItem()
        new_item.create_new(existing_item, spec)
        
        new_item.update(SloeVideoUtil.detect_video_params(new_item.get_file_path()))
        parent_album.add_child_obj(new_item)
        new_item.save_to_file()    
        
        
    @classmethod
    def find_remoteitem(cls, item, transferspec):
        common_id = "I=%s,T=%s" % (item.uuid, transferspec.uuid)
        spec = {
            "_primacy" : item._primacy,
            "_worth" : item._worth,
            "_subtree" : item._subtree,
            "common_id" : common_id,
            "name" : item.name
        }
        existing_remoteitem = SloeTreeUtil.find_remoteitem_by_spec(spec)
        remoteitem = SloeRemoteItem()
        remoteitem.create_new(existing_remoteitem, spec)        
        return remoteitem
    
        
    @classmethod
    def find_remoteplaylist(cls, playlist):
        common_id = "P=%s" % (playlist.uuid)
        spec = {
            "_primacy" : playlist._primacy,
            "_worth" : playlist._worth,
            "_subtree" : playlist._subtree,
            "common_id" : common_id,
            "name" : playlist.name
        }
        existing_remoteplaylist = SloeTreeUtil.find_remoteplaylist_by_spec(spec)
        remoteplaylist = SloeRemotePlaylist()
        remoteplaylist.create_new(existing_remoteplaylist, spec)        
        return remoteplaylist
    
        
    @classmethod
    def create_remoteitem_ini(cls, item, remoteitem):
        parent_album = SloeTreeUtil.find_album_by_uuid(item._parent_album_uuid)
        parent_album.add_child_obj(remoteitem)
        remoteitem.save_to_file()
        
    
    @classmethod
    def create_remoteplaylist_ini(cls, playlist, remoteplaylist):
        parent_album = SloeTreeUtil.find_album_by_uuid(playlist._parent_album_uuid)
        parent_album.add_child_obj(remoteplaylist)
        remoteplaylist.save_to_file()
        
    
    @classmethod
    def node_list_for_item(cls, parent_album, item):
        node_list = []
        for album in SloeTreeUtil.walk_parents(parent_album):
            node_list.append(album)
        if item is not None:
            node_list.append(item)
        return node_list
        

    @classmethod
    def substitute_for_remote_item(cls, value, final_item, remoteitem, transferspec):
        extracted = SloeUtil.extract_common_id(final_item.common_id)
        genspec = SloeTreeUtil.find_genspec(extracted["G"])
        origin_item = SloeTreeUtil.find_item(extracted["I"])
        outputspec = SloeTreeUtil.find_outputspec(extracted["O"])
        
        final_album = SloeTreeUtil.find_album_by_uuid(final_item._parent_album_uuid)
        origin_album = SloeTreeUtil.find_album_by_uuid(final_album.source_album_uuid)

        node_dict =  {
            "localitem": final_item,
            "originitem": origin_item,
            "localalbum": final_album,
            "originalbum": origin_album,
            "genspec": genspec,
            "outputspec": outputspec,
            "remoteitem": remoteitem,
            "origintree": cls.node_list_for_item(origin_album, origin_item),
            "localtree": cls.node_list_for_item(final_album, final_item)
        }
        
        return SloeVarUtil.substitute_from_node_dict(value, node_dict)
        

    @classmethod
    def substitute_for_remote_playlist(cls, value, final_playlist, remoteplaylist):

        final_album = SloeTreeUtil.find_album_by_uuid(final_playlist._parent_album_uuid)
        origin_album = SloeTreeUtil.find_album_by_uuid(final_album.source_album_uuid)

        node_dict =  {
            "localalbum": final_album,
            "originalbum": origin_album,
            "remoteplaylist": remoteplaylist,
            "origintree": cls.node_list_for_item(origin_album, None),
            "localtree": cls.node_list_for_item(final_album, final_playlist)
        }
        
        return SloeVarUtil.substitute_from_node_dict(value, node_dict)
