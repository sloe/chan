
import logging
import os
import re
import sys
from pprint import pprint, pformat

import sloelib

class SloePluginPlaylist(sloelib.SloeBasePlugIn):  
    
    def command_lslist(self, params, options):
        tree = sloelib.SloeTree.inst()
        tree.load()
        
        for subtree, album, items in sloelib.SloeTreeUtil.walk_items(tree.root_album):
            indent = ""
            if sloelib.SloeTreeUtil.object_matches_selector(album, params):
                try:
                    for playlist in album.playlists:
                        print "%s%s  Playlist: %s '%s'" % (playlist.uuid[:8], " " * len(indent), playlist.get_full_subtree(), playlist.title)

                        for item in playlist.get_ordered_items():
                            print "%s%s    Item: %s %s" % (item.uuid[:8], " " * len(indent), item.get_full_subtree(), item.get("title", item.name))
                         
    
                except KeyError, e:
                    logging.error("Missing attribute for %s (%s)" % (album.get("name", "<Unknown>"), str(e)))
                    raise e     
            

SloePluginPlaylist("playlist")
