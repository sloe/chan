
import logging
import os
from pprint import pformat, pprint
import uuid

from sloealbum import SloeAlbum
from sloeconfig import SloeConfig
from sloeerror import SloeError
from sloeitem import SloeItem
from sloetree import SloeTree
from sloetrees import SloeTrees


class SloeTreeUtil(object):
    def __init__(self, tree):
        self.tree = tree
        glb_cfg = SloeConfig.inst()
        self.verbose = SloeConfig.get_option("verbose")

                
    @classmethod 
    def walk_albums(cls, album):
        yield album
        for subalbum in album.subalbums:
            for x in cls.walk_albums(subalbum):
                yield x
                
                
                
    @classmethod 
    def walk_items(cls, album, subtree=[]):   
        new_subtree = subtree + [album.name]
        yield ("/".join(new_subtree), album, album.items)
            
        for subalbum in album.subalbums:
            for x in cls.walk_items(subalbum, new_subtree):
                yield x
                
                        
    @classmethod
    def walk_parents(cls, album):
        parent_uuid = album.get("_parent_album_uuid", None)
        if parent_uuid:
            parent_album = SloeTrees.inst().find_album_or_none(parent_uuid)
            if parent_album:
                for x in cls.walk_parents(parent_album):
                    yield x
        yield album
        

    @classmethod
    def get_genspec_uuid_for_outputspec(cls, outputspec):
        genspec_uuid = outputspec.get("genspec_uuid", None)
        if genspec_uuid is None:
            genspec_name = outputspec.get("genspec_name", None)
            if not genspec_name:
                raise SloeError("OutputSpec %s '%s' missing both genspec_name and genspec_uuid" % (outputspec.uuid, outputspec.name))
            genspec_uuid = SloeTreeUtil.find_genspec_uuid_by_name(SloeTree.inst().root_album, genspec_name)    
        return genspec_uuid
    
        
    @classmethod 
    def get_parent_outputspecs(cls, album):
        outputspecs = []
        for parent_album in cls.walk_parents(album):
            outputspecs += parent_album.outputspecs

        return outputspecs
    
    
    @classmethod 
    def find_genspec_uuid_by_name(cls, album, genspec_name):
        for album in SloeTreeUtil.walk_albums(album):
            for obj in album.genspecs:
                if obj.name == genspec_name:
                    return obj.uuid
        raise SloeError("GenSpec not found for name '%s'" % genspec_name)
    
    
    @classmethod 
    def find_genspec(cls, album, obj_uuid):
        for album in SloeTreeUtil.walk_parents(album):
            for obj in album.genspecs:
                if obj.uuid == obj_uuid:
                    return obj
                    
        raise SloeError("GenSpec not found for %s" % obj_uuid)
    
    
    @classmethod 
    def find_item(cls, album, obj_uuid):
        for album in SloeTreeUtil.walk_parents(album):
            for obj in album.items:
                if obj.uuid == obj_uuid:
                    return obj
                    
        raise SloeError("Item not found for %s" % obj_uuid)

      
    @classmethod 
    def find_album_and_item(cls, item_uuid):
        for album in cls.walk_albums(SloeTree.inst().root_album):
            item = album.item_dict.get(item_uuid)
            if item:
                return (album, item)

        raise SloeError("Item not found for %s" % item_uuid)      
        
        
    @classmethod 
    def find_outputspec(cls, album, obj_uuid):
        for album in SloeTreeUtil.walk_parents(album):
            for obj in album.outputspecs:
                if obj.uuid == obj_uuid:
                    return obj
                    
        raise SloeError("OutputSpec not found for %s" % obj_uuid)
    

    @classmethod
    def find_album_by_uuid(cls, uuid):
        for album in SloeTreeUtil.walk_albums(SloeTree.inst().get_root_album()):
            if album.uuid == uuid:
                return album
            
        return None


    @classmethod
    def find_album_by_spec(cls, spec):
        for album in SloeTreeUtil.walk_albums(SloeTree.inst().get_root_album()):
            found = True
            for k, v in spec.iteritems():
                if album.get(k, None) != v:
                    found = False
                    break
                
            if found:    
                return album
            
        return None


    @classmethod
    def find_item_by_spec(cls, spec):
        for subtree, album, items in SloeTreeUtil.walk_items(SloeTree.inst().get_root_album()):
            
            for item in items:
                found = True
                
                for k, v in spec.iteritems():
                    if item.get(k, None) != v:
                        found = False
                        break
                    
                if found:    
                    return item
            
        return None


    @classmethod
    def find_or_create_derived_album(cls, source_album_uuid, dest_treelist):
        source_album = cls.find_album_by_uuid(source_album_uuid)
        if source_album is None:
            raise SloeError("Parent album cannot be found for item %s" % source_album_uuid)
        findspec = {
            "source_album_uuid" : source_album.uuid
        }
        if len(dest_treelist) == 0:
            # Reached the top of the subtree, so return the top-level album
            toplevel_album = SloeTree.inst().get_root_album()
            if len(toplevel_album.subalbums) > 0:
                toplevel_album = toplevel_album.subalbums[0]
            return toplevel_album
        if len(dest_treelist) >= 1:
            findspec["_primacy"] = dest_treelist[0]
        if len(dest_treelist) >= 2:
            findspec["_worth"] = dest_treelist[1]
        if len(dest_treelist) >= 3:
            findspec["_subtree"] = "/".join(dest_treelist[2:])
                                            
        found_album = cls.find_album_by_spec(findspec)
        if found_album:
            logging.info("Found matching album %s" % found_album.uuid)
            return found_album
        
        # Create album, recursing to create its parents if necessary
        dest_parent = cls.find_or_create_derived_album(source_album._parent_album_uuid, dest_treelist[:-1])
        
        dest_path = os.path.join(SloeConfig.get_global("treeroot"), *dest_treelist)
        new_album = SloeAlbum()
        new_album.create_new(source_album.name, dest_path)
        new_album.update(findspec) 
        dest_parent.add_child_album(new_album)
        new_album.save_to_file()        
        return new_album
    