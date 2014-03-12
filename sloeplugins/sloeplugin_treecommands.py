
import logging
import os
import sys
from pprint import pprint, pformat

import sloelib

class SloePluginTreeCommands(object):
    
    def command_dotrans(self, params, options):
        tree = sloelib.SloeTree.inst()
        tree.load() 
        executor = sloelib.SloeLocalExec(tree)
        work_manager = sloelib.SloeWorkManager()
        selectors = params
        work, stats = work_manager.get_all_transfer_work(selectors)
        sloelib.SloeExecUtil.do_work(executor, work)
        
        
    def command_dowork(self, params, options):
        tree = sloelib.SloeTree.inst()
        tree.load() 
        executor = sloelib.SloeLocalExec(tree)
        work_manager = sloelib.SloeWorkManager()
        selectors = params
        work, stats = work_manager.get_all_work(selectors)
        sloelib.SloeExecUtil.do_work(executor, work)  
   
   
    def command_lstree(self, params, options):
        tree = sloelib.SloeTree.inst()
        tree.load()
        
        for subtree, album, items in sloelib.SloeTreeUtil.walk_items(tree.root_album):
            album_printed = False            
            
            def print_album():
                
                    print "%s%sAlbum: %s '%s' (%s)" % (album.uuid[:8], "-" * len(indent), album.name, album.title, album._location.replace("\\", "/"))
                    if options.verbose:
                        pprint(album._d)
                    
            indent = "  " * subtree.count("/")
            try:
                if sloelib.SloeTreeUtil.object_matches_selector(album, params):
                    if not album_printed:
                        print_album()
                        album_printed = True
                        
                for item in items:
                    if sloelib.SloeTreeUtil.object_matches_selector(item, params):                        
                        item_spec = ("%sx%s %sFPS %.2fs %.1fMB" %
                                     (item.video_width, item.video_height, item.video_avg_frame_rate, float(item.video_duration), float(item.video_size) / 2**20))
                        if not album_printed:
                            print_album()
                            album_printed = True
                        print "%s%s  %s (%s %s)" % (item.uuid[:8], indent, item.name, os.path.splitext(item.leafname)[1], item_spec)
                        if options.verbose:
                            pprint(item._d)
    
                for obj in album.genspecs:
                    if sloelib.SloeTreeUtil.object_matches_selector(obj, params):
                        if not album_printed:
                            print_album()
                            album_printed = True
                        print "%s%s  GenSpec: %s" % (obj.uuid[:8], "+" * len(indent), obj.name)
                        if options.verbose:
                            pprint(obj._d)
        
                for obj in album.outputspecs:
                    if sloelib.SloeTreeUtil.object_matches_selector(obj, params):
                        if not album_printed:
                            print_album()
                            album_printed = True
                        print "%s%s  OutputSpec: %s" % (obj.uuid[:8], "+" * len(indent), obj.name)
                        if options.verbose:
                            pprint(obj._d)
                            
                            
                for obj in album.remoteitems:
                    if sloelib.SloeTreeUtil.object_matches_selector(obj, params):
                        if not album_printed:
                            print_album()
                            album_printed = True
                        print "%s%sR %s %s" % (obj.uuid[:8], indent, obj.name, obj.remote_url)
                        if options.verbose:
                            pprint(obj._d)                              
                            
                            
                for obj in album.transferspecs:
                    if sloelib.SloeTreeUtil.object_matches_selector(obj, params):
                        if not album_printed:
                            print_album()
                            album_printed = True
                        print "%s%s  TransferSpec: %s" % (obj.uuid[:8], "+" * len(indent), obj.name)
                        if options.verbose:
                            pprint(obj._d)                
        
            except Exception, e:
                logging.error("Missing attribute for %s" % album.get("name", "<Unknown>"))
                raise e   
   
   
    def command_lswork(self, params, options):
        tree = sloelib.SloeTree.inst()
        tree.load()   
        work_manager = sloelib.SloeWorkManager()
        (work, stats) = work_manager.get_all_work(params)
        for job in work:
            extracted = sloelib.SloeUtil.extract_common_id(job.common_id)
            item_uuid = extracted["I"]
            album, item = sloelib.SloeTreeUtil.find_album_and_item(item_uuid)
            print "Render item pri=%.0f '%s/%s' using outputspec %s" % (job.priority, item._subtree, item.name, extracted["O"])
            
        print "Work items to do = %d, already done = %d" % (stats["todo"], stats["done"])
   
   
   
    def command_lstrans(self, params, options):
        tree = sloelib.SloeTree.inst()
        tree.load()   
        work_manager = sloelib.SloeWorkManager()
        (work, stats) = work_manager.get_all_transfer_work(params)
        for job in work:
            extracted = sloelib.SloeUtil.extract_common_id(job.common_id)
            item_uuid = extracted["I"]
            album, item = sloelib.SloeTreeUtil.find_album_and_item(item_uuid)
            print "Transfer item pri=%.0f '%s/%s' using transferspec %s" % (job.priority, item._subtree, item.name, extracted["T"])
            
        print "Transfer items to do = %d, already done = %d" % (stats["todo"], stats["done"])
   
      
   
    def process_obj(self, obj):
        for k in ("primacy", "worth", "subtree"):
            if k in obj._d:
                del obj._d[k]
   
   
    def command_refreshtree(self, params, options):
        tree = sloelib.SloeTree.inst()
        tree.load()
        for subtree, album, items in sloelib.SloeTreeUtil.walk_items(tree.root_album):
            for obj in items:
                self.process_obj(obj)
                obj.save_to_file()
                
            for obj in album.genspecs:
                self.process_obj(obj)
                obj.save_to_file()
                
            for obj in album.outputspecs:
                self.process_obj(obj)
                obj.save_to_file()
                        
            if album.name != "{root}":
                self.process_obj(album)
                album.save_to_file()                
                
    
    @classmethod
    def register(cls):
        obj = SloePluginTreeCommands()
        spec = {
            "methods": {
                "command_dotrans" : cls.command_dotrans,
                "command_dowork" : cls.command_dowork,
                "command_lstrans" : cls.command_lstrans,
                "command_lstree" : cls.command_lstree,
                "command_lswork" : cls.command_lswork,
                "command_refreshtree" : cls.command_refreshtree
            },
            "object": obj
        }
        sloelib.SloePlugInManager.inst().register_plugin("treecommands", spec)
        

SloePluginTreeCommands.register()
