
import logging
import os
import re
import sys
from pprint import pprint, pformat
import uuid

import sloelib

class SloePluginOarstack(sloelib.SloeBasePlugIn):  
    
    def command_makeprimary(self, params, options):
        pprint(params)
        event_dir, day_dir, div_dir = params
        div_code = "%s%s" % (div_dir[3].upper(), div_dir[4])
        root_dir = sloelib.SloeConfig.inst().get_global("treeroot")
        primary_path = os.path.join(root_dir, 'primary', 'derived', event_dir, day_dir, div_dir)
        final_path = os.path.join(root_dir, 'final', 'derived', event_dir, day_dir, div_dir)
        if not os.path.exists(os.path.dirname(primary_path)):
            raise sloelib.SloeError("Primary path '%s' missing" % primary_path)
        if not os.path.exists(os.path.dirname(final_path)):
            raise sloelib.SloeError("Final path '%s' missing" % final_path)
            
        if os.path.exists(primary_path):
            raise sloelib.SloeError("Dir %s already exists" % primary_path)
        else:
            os.mkdir(primary_path)
        
        if os.path.exists(final_path):
            raise sloelib.SloeError("Dir %s already exists" % final_path)
        else:
            os.mkdir(final_path)
            
        primary_album = sloelib.SloeAlbum()
        primary_album.create_new(div_dir, primary_path)
        primary_album.set_values(
            title=div_code,
            subevent_title=div_code
        )
        primary_album.save_to_file()

        final_album = sloelib.SloeAlbum()
        final_album.create_new(div_dir, final_path)
        final_album.set_values(
            title=div_code,
            source_album_uuid = primary_album.uuid
        )
        final_album.save_to_file()        
        
        def make_playlist(subname, title, selector, short_speed, long_speed, tags):
            playlist = sloelib.SloePlaylist()
            playlist.create_new("+%s-%s" % (div_dir, subname), "1000", final_path)
            playlist.set_values(
                title=title,
                transfer_type="youtube",
                youtube_description="#{ join(\" \", origintree.event_title ) } #{ join(\" \", origintree.subevent_title ) } %s(#{ closest(origintree.event_time) }, #{ closest(origintree.location) })\n\nContact: info@oarstack.com" % long_speed,
                youtube_privacy="public",
                youtube_tags="#{ join(\",\", origintree.tags) }%s" % tags,
                youtube_title="#{ join(\" \", origintree.event_title, origintree.subevent_title ) } %s [#{ closest(origintree.sitetag) }]" % short_speed
            )
            if selector is not None:
                playlist.set_values(selector_genspec_name=selector)
            pprint(playlist)
            playlist.save_to_file()
        
        make_playlist("all", "Cambridge May Bumps 2014 Division %s" % div_code, None, "normal and slow motion", "alternating normal speed and slow motion ", ",Slow Motion")
        make_playlist("ytf", "Cambridge May Bumps 2014 Division %s normal speed" % div_code, "youtube,I=60p,S=1", "normal speed", "", "")
        make_playlist("ytq", "Cambridge May Bumps 2014 Division %s slow motion" % div_code, "youtube,I=60p,S=4", "slow motion", "slow motion ", ",Slow Motion")
                        

SloePluginOarstack("oarstack")
