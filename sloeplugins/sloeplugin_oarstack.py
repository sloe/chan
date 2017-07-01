
import glob
import logging
import os
import re
import sys
from pprint import pprint, pformat
import uuid

import sloelib

class SloePluginOarstack(sloelib.SloeBasePlugIn):

    CURRENT_YEAR = 2012
    CAPTURE_DEVICE = "Sony Alpha A9 camera" # e.g. "Sony Alpha A9 camera"
    CAPTURE_INFO = "1080p/120fps" # e.g. "1080p/120fps"
    LOCATION = "Cambridge, UK" # e.g. "Cambridge, UK"
    EVENT_TITLE = "May Bumps 2017" # e.g. "May Bumps 2017"
    TAGS = "Rowing (Sport),Cambridge,May Bumps 2017" # e.g. "Rowing (Sport),Cambridge,May Bumps 2017"
    TITLE = "May Bumps 2017" # e.g. "May Bumps 2017"

    def command_makemays(self, params, options):
        pprint(params)
        event_dir, day_dir, div_dir = params
        div_code = "%s%s" % (div_dir[3].upper(), div_dir[4])
        root_dir = sloelib.SloeConfig.inst().get_global("treeroot")
        primary_path = os.path.join(root_dir, 'primary', 'precious', event_dir, day_dir, div_dir)
        final_path = os.path.join(root_dir, 'final', 'derived', event_dir, day_dir, div_dir)
        if not os.path.exists(os.path.dirname(primary_path)):
            raise sloelib.SloeError("Primary path '%s' missing" % os.path.dirname(primary_path))
        if not os.path.exists(os.path.dirname(final_path)):
           os.mkdir(os.path.dirname(final_path))

        if os.path.exists(primary_path):
            if glob.glob(os.path.join(primary_path, '*ALBUM*ini')):
                pass #raise sloelib.SloeError("Album %s already exists" % primary_path)
        else:
            os.mkdir(primary_path)

        if os.path.exists(final_path):
            if glob.glob(os.path.join(final_path, '*ALBUM*ini')):
                pass # raise sloelib.SloeError("Album %s already exists" % final_path)
        else:
            os.mkdir(final_path)

        primary_event_path = os.path.join(root_dir, 'primary', 'derived', event_dir)
        primary_day_path = os.path.join(root_dir, 'primary', 'derived', event_dir, day_dir)
        final_event_path = os.path.join(root_dir, 'final', 'derived', event_dir)
        final_day_path = os.path.join(root_dir, 'final', 'derived', event_dir, day_dir)

        if not glob.glob(os.path.join(primary_event_path, '*ALBUM*ini')):
            primary_album = sloelib.SloeAlbum()
            primary_album.create_new(div_dir, primary_event_path)
            primary_album.set_values(
                name=event_dir,
                capture_device=CAPTURE_DEVICE,
                capture_info=CAPTURE_INFO,
                location=LOCATION,
                event_title=EVENT_TITLE,
                tags=TAGS,
                title=TITLE
            )
            primary_album.save_to_file()


        if not glob.glob(os.path.join(final_event_path, '*TRANSFERSPEC*ini')):
            div_transferspec = sloelib.SloeTransferSpec()
            div_transferspec.create_new()
            div_transferspec.set_values(
                name="%s-yt-div" % event_dir,
                priority="1000",
                transfer_type="youtube",
                selectors="final/*/%s/*/div*" % event_dir,
                # Category 17 is Sport
                youtube_category="17",
                youtube_description='#{ join(" ", origintree.event_title ) } #{ join(" ", origintree.subevent_title ) }, Crew #{ join(" ", originitem.name) } (#{ closest(origintree.event_time) }, #{ closest(origintree.location) })\n\nAnalysis: http://analysis.oarstack.com/yt/#{localitem.uuid}\n\nCapture: #{ closest(origintree.capture_device) } #{ closest(origintree.capture_info) }\nThis render: #{ join(".  ", genspec.output_description, genspec.output_note) }.\n\nContact: info@oarstack.com quoting reference #{remoteitem.uuid}.',
                youtube_privacy="public",
                youtube_tags='#{ join(",", origintree.tags) },Slow Motion,yt:quality=high',
                youtube_title='#{ originitem.name }, #{ join(" ", origintree.event_title, genspec.output_short_description) } [#{ closest(origintree.sitetag) }]'

            )
            div_transferspec.add_filepath_info(os.path.join(final_event_path, 'dummy'))
            div_transferspec.save_to_file()


        if not glob.glob(os.path.join(primary_path, '*ALBUM*ini')):
            if glob.glob(os.path.join(final_path, '*ALBUM*ini')):
                raise sloelib.SloeError("Final album present with no primary (%s, %s)" % (primary_path, final_path))

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


        if not glob.glob(os.path.join(final_path, '*ALBUM*ini')):
            raise sloelib.SloeError("Final album missing from %s" % final_path)


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


        if not glob.glob(os.path.join(final_path, '*PLAYLIST*ini')):
            make_playlist("all", "Cambridge May Bumps %d division %s" % (self.CURRENT_YEAR, div_code), None, "normal and slow motion", "alternating normal speed and slow motion ", ",Slow Motion")
            if self.CURRENT_YEAR > 2016:
                # 120fps era
                make_playlist("ytf", "Cambridge May Bumps %d division %s normal speed" % (self.CURRENT_YEAR, div_code), "youtube,I=120p,S=1", "normal speed", "", "")
                make_playlist("yt8", "Cambridge May Bumps %d division %s slow motion" % (self.CURRENT_YEAR, div_code), "youtube,I=120p,S=8", "slow motion", "slow motion ", ",Slow Motion")
            elif self.CURRENT_YEAR == 2012:
                # 720p/50fps
                make_playlist("ytf", "Cambridge May Bumps %d division %s normal speed" % (self.CURRENT_YEAR, div_code), "youtube720,I=50p,S=1", "normal speed", "", "")
                make_playlist("ytq", "Cambridge May Bumps %d division %s slow motion" % (self.CURRENT_YEAR, div_code), "youtube720,I=50p,S=4", "slow motion", "slow motion ", ",Slow Motion")
            else:
                # 60fps era
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
