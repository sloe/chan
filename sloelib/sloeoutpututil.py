
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
        
        while True:
            match = re.match(r'(.*){(\w*)}(.*)', output_path)
            if not match:
                break
            name = match.group(2)
            if name not in replacements:
                raise SloeError("No substitution variable {%s} - options are %s" % (name, ",".join(replacements.keys())))
            output_path = match.group(1) + replacements[name] + match.group(3)
    
        return output_path
    
                
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
    def create_remoteitem_ini(cls, item, transferspec, remote_id, remote_url):
        parent_album = SloeTreeUtil.find_album_by_uuid(item._parent_album_uuid)
        
        common_id = "I=%s,T=%s" % (item.uuid, transferspec.uuid)
        spec = {
            "_primacy" : item._primacy,
            "_worth" : item._worth,
            "_subtree" : item._subtree,
            "common_id" : common_id,
            "name" : item.name
        }
        existing_remoteitem = SloeTreeUtil.find_remoteitem_by_spec(spec)
        logging.info("existing remoteitem=%s"% pformat(existing_remoteitem))
        spec.update({
            "remote_id": remote_id,
            "remote_url": remote_url            
        })
        remoteitem = SloeRemoteItem()
        remoteitem.create_new(existing_remoteitem, spec)
        
        parent_album.add_child_remoteitem(remoteitem)
        remoteitem.save_to_file()
        