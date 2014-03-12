
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
from sloetree import SloeTree
from sloetreeutil import SloeTreeUtil
from sloeutil import SloeUtil
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

        for album in album.subalbums:
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
        parent_album.add_child_item(new_item)
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
    def create_remoteitem_ini(cls, item, remoteitem):
        parent_album = SloeTreeUtil.find_album_by_uuid(item._parent_album_uuid)
        parent_album.add_child_remoteitem(remoteitem)
        remoteitem.save_to_file()
        
    
    
    @classmethod
    def substitute_from_tree(cls, input_string, node_name, parent_album, item):
        nodes = [item]
        for album in SloeTreeUtil.walk_parents(parent_album):
            nodes.append(album)
            
        return SloeUtil.substitute_from_node_list(input_string, node_name, nodes)    


    @classmethod
    def get_item_description(cls, item, remoteitem, transferspec):
        replacements = {}
        
        replacements.update(cls.replacements_for_item(item))
        
        return SloeUtil.substitute_vars(transferspec.description_merge, replacements)
        

    @classmethod
    def get_item_title(cls, item, remoteitem, transferspec):
        extracted = SloeUtil.extract_common_id(item.common_id)
        genspec = SloeTreeUtil.find_genspec(SloeTree.inst().root_album, extracted["G"])
        source_item = SloeTreeUtil.find_item(SloeTree.inst().root_album, extracted["I"])
        outputspec = SloeTreeUtil.find_outputspec(SloeTree.inst().root_album, extracted["O"])
        
        dest_album = SloeTreeUtil.find_album_by_uuid(item._parent_album_uuid)
        source_album = SloeTreeUtil.find_album_by_uuid(dest_album.source_album_uuid)
        
        value = transferspec.title_merge
        value = SloeUtil.substitute_from_node_list(value, "destitem", item)
        value = SloeUtil.substitute_from_node_list(value, "sourceitem", source_item)
        value = SloeUtil.substitute_from_node_list(value, "destalbum", dest_album)
        value = SloeUtil.substitute_from_node_list(value, "sourcealbum", source_album)
        value = SloeUtil.substitute_from_node_list(value, "genspec", genspec)
        value = SloeUtil.substitute_from_node_list(value, "outputspec", outputspec)
        value = cls.substitute_from_tree(value, "sourcetree", source_album, item)
        value = cls.substitute_from_tree(value, "desttree", dest_album, item)
        replacements = {}
        
        replacements.update(cls.replacements_for_item(source_album, dest_album, source_item, dest_item))
        
        return SloeUtil.substitute_vars(value, replacements)
