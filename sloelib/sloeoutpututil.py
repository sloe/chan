
import logging
import os
from pprint import pformat, pprint
import re
import uuid

from sloealbum import SloeAlbum
from sloeconfig import SloeConfig
from sloeerror import SloeError
from sloeitem import SloeItem
from sloetree import SloeTree
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
    def get_output_path(self, genspec, item, outputspec):
        output_path = outputspec.output_path

        replacements = {
            "basename" : os.path.splitext(os.path.basename(item.leafname))[0],
            "ext" : genspec.output_extension,
            "suffix" : genspec.output_suffix,
            "name" : item.name,
            "subtree" : item.subtree,
            }
        
        while True:
            match = re.match(r'(.*){(\w*)}(.*)', output_path)
            if not match:
                break
            name = match.group(2)
            if name not in replacements:
                raise SloeError("No substitution variable {%s} - options are %s" % (name, ",".join(replacements.keys())))
            output_path = match.group(1) + replacements[name] + match.group(3)
                
        
        if not re.match(r'[\\/]', output_path) and not re.match(r'[A-Z]:[\\/]', output_path):
            output_path = os.path.join(SloeConfig.get_global("treeroot"), output_path)
            
        return output_path
    
    @classmethod
    def create_output_ini(cls, genspec, item, outputspec):
        current_tree = SloeTree.inst()
        common_id = "G=%s,I=%s,O=%s" % (genspec.uuid, item.uuid, outputspec.uuid)
        spec = {
            "common_id" : common_id,
            "leafname" : os.path.basename(cls.get_output_path(genspec, item, outputspec)),
            "name" : item.name,
            "parent_uuid" : item.parent_uuid,
            "primacy" : outputspec.primacy,
            "subtree" : item.subtree,
            "worth" : outputspec.worth
        }
        existing_item = current_tree.get_item_from_spec(spec)
        logging.info("exisiting item=%s"% pformat(existing_item))
        item = SloeItem()
        item.create_new(existing_item, spec)
        
        item.update(SloeVideoUtil.detect_video_params(item.get_file_path()))
        item.save_to_file()    
        