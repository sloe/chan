
import logging
import os
import sys
from pprint import pprint, pformat

import sloelib

class SloePluginShowCommands(sloelib.SloeBasePlugIn):
    
    
    def command_showlist(self, params, options):
        tree = sloelib.SloeTree.inst()
        tree.load()
        
        for subtree, album, items in sloelib.SloeTreeUtil.walk_items(tree.root_album):
            indent = "  " * subtree.count("/")
            try:
                for obj in album.playlists:
                    print "%s%s  Playlist: %s" % (obj.uuid[:8], " " * len(indent), obj.name)

            except Exception, e:
                logging.error("Missing attribute for %s" % album.get("name", "<Unknown>"))
                raise e                   


SloePluginShowCommands("showcommands")
    