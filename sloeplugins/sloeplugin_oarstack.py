
import logging
import os
import re
import sys
from pprint import pprint, pformat
import uuid

import sloelib

class SloePluginOarstack(sloelib.SloeBasePlugIn):

    CURRENT_YEAR = 2016

    def command_makemays(self, params, options):
        pprint(params)
        event_dir, day_dir, div_dir = params
        div_code = "%s%s" % (div_dir[3].upper(), div_dir[4])
        root_dir = sloelib.SloeConfig.inst().get_global("treeroot")
        primary_path = os.path.join(root_dir, 'primary', 'derived', event_dir, day_dir, div_dir)
        final_path = os.path.join(root_dir, 'final', 'derived', event_dir, day_dir, div_dir)
        if not os.path.exists(os.path.dirname(primary_path)):
            raise sloelib.SloeError("Primary path '%s' missing" % os.path.dirname(primary_path))
        if not os.path.exists(os.path.dirname(final_path)):
            raise sloelib.SloeError("Final path '%s' missing" % os.path.dirname(final_path))

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
            title="division %s" % div_code,
            subevent_title="division %s" % div_code
        )
        primary_album.save_to_file()

        final_album = sloelib.SloeAlbum()
        final_album.create_new(div_dir, final_path)
        final_album.set_values(
            title="division %s" % div_code,
            source_album_uuid = primary_album.uuid
        )
        final_album.save_to_file()

        def make_playlist(subname, title, selector, short_speed, long_speed, tags):
            playlist = sloelib.SloePlaylist()
            playlist.create_new("+%s-%s" % (div_dir, subname), title, "1000", final_path)
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

        make_playlist("all", "Cambridge May Bumps %d division %s" % (self.CURRENT_YEAR, div_code), None, "normal and slow motion", "alternating normal speed and slow motion ", ",Slow Motion")
        make_playlist("ytf", "Cambridge May Bumps %d division %s normal speed" % (self.CURRENT_YEAR, div_code), "youtube,I=60p,S=1", "normal speed", "", "")
        make_playlist("ytq", "Cambridge May Bumps %d division %s slow motion" % (self.CURRENT_YEAR, div_code), "youtube,I=60p,S=4", "slow motion", "slow motion ", ",Slow Motion")



    def command_makeevent(self, params, options):
        pprint(params)
        event_name, event_dir, div_dir = params
        div_code = div_dir
        root_dir = sloelib.SloeConfig.inst().get_global("treeroot")
        primary_path = os.path.join(root_dir, 'primary', 'derived', event_dir, div_dir)
        final_path = os.path.join(root_dir, 'final', 'derived', event_dir, div_dir)
        if not os.path.exists(os.path.dirname(primary_path)):
            raise sloelib.SloeError("Primary path '%s' missing" % os.path.dirname(primary_path))
        if not os.path.exists(os.path.dirname(final_path)):
            raise sloelib.SloeError("Final path '%s' missing" % os.path.dirname(final_path))

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
            title="division %s" % div_code,
            subevent_title="division %s" % div_code
        )
        primary_album.save_to_file()

        final_album = sloelib.SloeAlbum()
        final_album.create_new(div_dir, final_path)
        final_album.set_values(
            title="division %s" % div_code,
            source_album_uuid = primary_album.uuid
        )
        final_album.save_to_file()

        def make_playlist(subname, title, selector, short_speed, long_speed, tags):
            playlist = sloelib.SloePlaylist()
            playlist.create_new("+%s-%s" % (div_dir, subname), title, "1000", final_path)
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

        make_playlist("all", "%s division %s" % (event_name, div_code), None, "normal and slow motion", "alternating normal speed and slow motion ", ",Slow Motion")
        make_playlist("ytf", "%s division %s normal speed" % (event_name, div_code), "youtube,I=60p,S=1", "normal speed", "", "")
        make_playlist("ytq", "%s division %s slow motion" % (event_name, div_code), "youtube,I=60p,S=4", "slow motion", "slow motion ", ",Slow Motion")



    def command_oarstacklist(self, params, options):
        tree = sloelib.SloeTree.inst()
        tree.load()

        for subtree, album, items in sloelib.SloeTreeUtil.walk_items(tree.root_album):
            indent = ""
            if sloelib.SloeTreeUtil.object_matches_selector(album, params):
                try:
                    for remoteplaylist in album.remoteplaylists:
                        ids = sloelib.SloeUtil.extract_common_id(remoteplaylist.common_id)
                        playlist = sloelib.SloeTreeNode.get_object_by_uuid(ids['P'])
                        title = playlist.title
                        if title[-1] in "0123456789":
                            title += " normal and slow motion"
                        print '<a title="%s" href="https://www.youtube.com/playlist?list=%s">%s</a>' % (title, remoteplaylist.remote_id, title)

                except KeyError, e:
                    logging.error("Missing attribute for %s (%s)" % (album.get("name", "<Unknown>"), str(e)))
                    raise e


SloePluginOarstack("oarstack")
