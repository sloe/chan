
import glob
import json
import logging
import os
from pprint import pprint, pformat
import re
import string
import subprocess

import sloelib

class SloePluginGenerateConfig(object):
   
    def command_generatecfg(self, params, options):
        for subtree in params:    
            self.process_tree(subtree)


    def process_tree(self, subtree):
        if sloelib.SloeConfig.get_option("final"):
            primacy = "final"
        else:
            primacy = "primary"

        
        treeroot = sloelib.SloeConfig.get_global("treeroot")
        primacy_tree = os.path.join(treeroot, primacy)
        self.process_dir("root", treeroot)        
        self.process_dir(primacy, primacy_tree)        
        for worth in sloelib.SloeConfig.get_global("worths").split(","):
            self.process_dir(worth, os.path.join(primacy_tree, worth))   
            
        for worth, walkroot in sloelib.SloeTrees.inst().get_treepaths(primacy, subtree).iteritems():
            logging.debug("generate_cfg walking tree directory %s" % walkroot)
            
            self.process_dir(os.path.basename(walkroot), walkroot)

            for dirpath, dirs, files in os.walk(walkroot, topdown=True, followlinks=False):
                for _dir in dirs:
                    self.process_dir(os.path.basename(_dir), os.path.join(dirpath, _dir))

            subtree_root = sloelib.SloeTrees.inst().get_treeroot(primacy, worth)

            for dirpath, dirs, files in os.walk(walkroot, topdown=True, followlinks=False):
                for filename in files:
                    match = re.match(r"^(.*)\.(flv|mp4|f4v)$", filename)
                    if match:
                        spec = {
                            "leafname" : filename,
                            "name" : match.group(1),
                            "_primacy" : primacy,
                            "_subtree" : string.replace(os.path.relpath(dirpath, subtree_root), "\\", "/"),
                            "_worth" : worth
                        }
                        self.process_file(spec)


    def process_dir(self, name, full_path):
        logging.debug("Processing directory %s" % full_path)
        if not os.path.exists(full_path):
            os.makedirs(full_path)        
        album_files = glob.glob(os.path.join(full_path, "*ALBUM=*.ini"))
        if album_files == []:
            # Find UUID of parent album
            parent_uuid = None
            parent_dir = full_path
            while parent_uuid is None:
                if parent_dir == os.path.dirname(parent_dir):
                    logging.error("Directory search reached root directory")
                    break
                parent_dir = os.path.dirname(parent_dir)
                
                album_files = glob.glob(os.path.join(parent_dir, "*ALBUM=*.ini"))     
                if len(album_files) > 1:
                    logging.error("More than one potential parent album in %s - please set in %s manually" % (parent_dir, full_path))
                    break
                if len(album_files) == 1:
                    temp_album = sloelib.SloeAlbum()
                    temp_album.create_from_ini_file(os.path.join(parent_dir, album_files[0]),
                                                            "Loading album to determine parent")
                    parent_uuid = temp_album.uuid

                if os.path.normpath(parent_dir).lower() == os.path.normpath(sloelib.SloeConfig.get_global("treeroot")).lower():
                    logging.error("Search for parent album abandoned in %s" % parent_dir)                    
                    break
                
 
            
            logging.debug("Creating template album file in %s" % full_path)
            album = sloelib.SloeAlbum()
            album.create_new(name, full_path)
            if parent_uuid is not None:
                logging.info("Found parent album for %s in %s UUID %s" % (full_path, parent_dir, parent_uuid))     
                album.set_value("_parent_album_uuid", parent_uuid)            
            if not sloelib.SloeConfig.get_option("dryrun"):
                album.save_to_file()


    def process_file(self, spec):
        logging.debug("Processing file with spec %s" % repr(spec))

        current_tree = sloelib.SloeTree.inst()
        existing_item = current_tree.get_item_from_spec(spec)
        item = sloelib.SloeItem()
        item.create_new(existing_item, spec)
        
        item.update(sloelib.SloeVideoUtil.detect_video_params(item.get_file_path()))
        if not sloelib.SloeConfig.get_option("dryrun"):
            item.save_to_file()
    
    
    @classmethod
    def register(cls):
        obj = SloePluginGenerateConfig()
        spec = {
            "methods": {
                "command_generatecfg" : cls.command_generatecfg
            },
            "object": obj
        }
        sloelib.SloePlugInManager.inst().register_plugin("generatecfg", spec)
        

SloePluginGenerateConfig.register()
