
import glob
import logging
import os
import re
import sys
from pprint import pprint, pformat
import uuid

import sloelib

class SloePluginOarstack(sloelib.SloeBasePlugIn):

    EVENT_DATA = dict(
        mays2011=dict(
            year=2011,
            capture_device="Canon XF100 camera",
            capture_info="720p/50fps",
            genspec_name_ytf="youtube720,I=50p,S=1",
            genspec_name_ytnf="youtube720,I=50p,S=4",
            location="Cambridge, UK",
            event_title="May Bumps 2011",
            tags="Rowing (Sport),Cambridge,May Bumps 2011",
            title="May Bumps 2011",
            wed=dict(
                title="Wednesday",
                subevent_title="Wednesday",
                event_time="Wednesday 15th June 2011"
            ),
            thurs=dict(
                title="Thursday",
                subevent_title="Thursday",
                event_time="Thursday 16th June 2011"
            ),
            fri=dict(
                title="Friday",
                subevent_title="Friday",
                event_time="Friday 17th June 2011"
            ),
            sat=dict(
                title="Saturday",
                subevent_title="Saturday",
                event_time="Saturday 18th June 2011"
            )
        ),
        mays2018=dict(
            year=2018,
            capture_device="Panasonic GH5S camera",
            capture_info="1080p/240fps",
            genspec_name_ytf="youtube,I=240p,S=1",
            genspec_name_ytnf="youtube,I=240p,S=16",
            location="Cambridge, UK",
            event_title="May Bumps 2018",
            tags="Rowing (Sport),Cambridge,May Bumps 2018",
            title="May Bumps 2018",
            wed=dict(
                title="Wednesday",
                subevent_title="Wednesday",
                event_time="Wednesday 13th June 2018"
            ),
            thurs=dict(
                title="Thursday",
                subevent_title="Thursday",
                event_time="Thursday 14th June 2018"
            )
        )
    )

    def command_makemays(self, params, options):
        pprint(params)
        event_dir, day_dir, div_dir = params
        event_data = self.EVENT_DATA[event_dir]
        current_year = event_data['year']
        div_code = "%s%s" % (div_dir[3].upper(), div_dir[4])
        root_dir = sloelib.SloeConfig.inst().get_global("treeroot")
        primary_div_path = os.path.join(root_dir, 'primary', 'derived', event_dir, day_dir, div_dir)
        primary_event_path = os.path.join(root_dir, 'primary', 'derived', event_dir)
        primary_day_path = os.path.join(root_dir, 'primary', 'derived', event_dir, day_dir)
        final_div_path = os.path.join(root_dir, 'final', 'derived', event_dir, day_dir, div_dir)
        final_event_path = os.path.join(root_dir, 'final', 'derived', event_dir)
        final_day_path = os.path.join(root_dir, 'final', 'derived', event_dir, day_dir)

        if not os.path.exists(primary_div_path):
            os.makedirs(primary_div_path)
        if not os.path.exists(final_div_path):
            os.makedirs(final_div_path)

        # Primary albums

        if not glob.glob(os.path.join(primary_event_path, '*ALBUM*ini')):
            # Create the primary top level event album
            primary_event_album = sloelib.SloeAlbum()
            primary_event_album.create_new(div_dir, primary_event_path)
            primary_event_album.set_values(
                name=event_dir,
                capture_device=event_data['capture_device'],
                capture_info=event_data['capture_info'],
                location=event_data['location'],
                event_title=event_data['event_title'],
                tags=event_data['tags'],
                title=event_data['title']
            )
            primary_event_album.save_to_file()


        if not glob.glob(os.path.join(primary_day_path, '*ALBUM*ini')):
            # Create the primary day level event album
            primary_day_album = sloelib.SloeAlbum()
            primary_day_album.create_new(day_dir, primary_day_path)
            primary_day_album.set_values(
                name=day_dir,
                event_time=event_data[day_dir]['event_time'],
                subevent_title=event_data[day_dir]['subevent_title'],
                title=event_data[day_dir]['title']
            )
            primary_day_album.save_to_file()


        if not glob.glob(os.path.join(primary_div_path, '*ALBUM*ini')):
            # Create the primary division level event album
            primary_div_album = sloelib.SloeAlbum()
            primary_div_album.create_new(div_dir, primary_div_path)
            primary_div_album.set_values(
                title="division %s" % div_code,
                subevent_title="division %s" % div_code
            )
            primary_div_album.save_to_file()

        # Final albums

        if not glob.glob(os.path.join(final_event_path, '*ALBUM*ini')):
            # Create the final top level event album
            final_event_album = sloelib.SloeAlbum()
            final_event_album.create_new(event_dir, final_event_path)
            final_event_album.set_values(
                source_album_uuid=primary_event_album.uuid,
                title=event_data['title']
            )
            final_event_album.save_to_file()


        if not glob.glob(os.path.join(final_day_path, '*ALBUM*ini')):
            # Create the final day album
            final_day_album = sloelib.SloeAlbum()
            final_day_album.create_new(day_dir, final_day_path)
            final_day_album.set_values(
                title=event_data[day_dir]['title'],
                source_album_uuid = primary_day_album.uuid
            )
            final_day_album.save_to_file()


        if not glob.glob(os.path.join(final_div_path, '*ALBUM*ini')):
            # Create the final division album
            final_div_album = sloelib.SloeAlbum()
            final_div_album.create_new(div_dir, final_div_path)
            final_div_album.set_values(
                name=div_dir,
                title="division %s" % div_code,
                source_album_uuid = primary_div_album.uuid
            )
            final_div_album.save_to_file()

        # Primary OutputSpecs

        if not glob.glob(os.path.join(primary_event_path, '*OUTPUTSPEC*ini')):
            # Create the event level output specs
            event_outputspec_ytf = sloelib.SloeOutputSpec()
            event_outputspec_ytf.create_new()
            event_outputspec_ytf.set_values(
                name="%s-ytf" % event_dir,
                genspec_name=event_data['genspec_name_ytf'],
                glob_include="*",
                output_path="final/derived/{subtree}/{basename}{suffix}{ext}",
                priority=1000
            )
            event_outputspec_ytf.add_filepath_info(os.path.join(primary_event_path, 'dummy'))
            event_outputspec_ytf.save_to_file()

            event_outputspec_ytnf = sloelib.SloeOutputSpec()
            event_outputspec_ytnf.create_new()
            event_outputspec_ytnf.set_values(
                name="%s-yt16" % event_dir,
                genspec_name=event_data['genspec_name_ytnf'],
                glob_include="*",
                output_path="final/derived/{subtree}/{basename}{suffix}{ext}",
                priority=500
            )
            event_outputspec_ytnf.add_filepath_info(os.path.join(primary_event_path, 'dummy'))
            event_outputspec_ytnf.save_to_file()

        # Final TransferSpecs

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


        if not glob.glob(os.path.join(final_div_path, '*ALBUM*ini')):
            raise sloelib.SloeError("Final album missing from %s" % final_div_path)


        def make_playlist(subname, title, selector, short_speed, long_speed, tags):
            playlist = sloelib.SloePlaylist()
            playlist.create_new("+%s-%s" % (div_dir, subname), title, "1000", final_div_path)
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


        if not glob.glob(os.path.join(final_div_path, '*PLAYLIST*ini')):
            make_playlist("all", "Cambridge May Bumps %d division %s" % (current_year, div_code), None, "normal and slow motion", "alternating normal speed and slow motion ", ",Slow Motion")
            if current_year > 2017:
                # 240fps era
                make_playlist("ytf", "Cambridge May Bumps %d division %s normal speed" % (current_year, div_code), "youtube,I=240p,S=1", "normal speed", "", "")
                make_playlist("yt16", "Cambridge May Bumps %d division %s slow motion" % (current_year, div_code), "youtube,I=240p,S=16", "slow motion", "slow motion ", ",Slow Motion")
            elif current_year > 2016:
                # 120fps era
                make_playlist("ytf", "Cambridge May Bumps %d division %s normal speed" % (current_year, div_code), "youtube,I=120p,S=1", "normal speed", "", "")
                make_playlist("yt8", "Cambridge May Bumps %d division %s slow motion" % (current_year, div_code), "youtube,I=120p,S=8", "slow motion", "slow motion ", ",Slow Motion")
            elif current_year == 2012:
                # 720p/50fps
                make_playlist("ytf", "Cambridge May Bumps %d division %s normal speed" % (current_year, div_code), "youtube720,I=50p,S=1", "normal speed", "", "")
                make_playlist("ytq", "Cambridge May Bumps %d division %s slow motion" % (current_year, div_code), "youtube720,I=50p,S=4", "slow motion", "slow motion ", ",Slow Motion")
            else:
                # 60fps era
                make_playlist("ytf", "Cambridge May Bumps %d division %s normal speed" % (current_year, div_code), "youtube,I=60p,S=1", "normal speed", "", "")
                make_playlist("ytq", "Cambridge May Bumps %d division %s slow motion" % (current_year, div_code), "youtube,I=60p,S=4", "slow motion", "slow motion ", ",Slow Motion")

        pass


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
