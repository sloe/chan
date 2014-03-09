
import datetime
import fnmatch
import logging
import os
from pprint import pformat, pprint
import uuid

from sloealbum import SloeAlbum
from sloeconfig import SloeConfig
from sloeerror import SloeError
from sloeitem import SloeItem
from sloeoutputspec import SloeOutputSpec
from sloerenderjob import SloeRenderJob
from sloetransferjob import SloeTransferJob
from sloetree import SloeTree
from sloetreeutil import SloeTreeUtil


class SloeWorkManager(object):
    def __init__(self):
        pass

    def get_work_for_item(self, album, item, outputspec):
        work = []
        stats_todo = 0
        stats_done = 0
        add_workspec = False
        glob_include = outputspec.get("glob_include", None)
        if fnmatch.fnmatch(item.leafname, glob_include) and item._primacy == "primary":
            add_workspec = True
            
        if add_workspec:
            genspec_uuid = SloeTreeUtil.get_genspec_uuid_for_outputspec(outputspec)
            common_id = "G=%s,I=%s,O=%s" % (genspec_uuid, item.uuid, outputspec.uuid)
            found_item = SloeTreeUtil.find_item_by_spec({
                "common_id": common_id
            })
            if found_item is not None:
                add_workspec = False
                stats_done += 1
                
        if add_workspec:          
            workspec = SloeRenderJob()
            workspec.set_values(
                name="workitem %s" % datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%SZ'),
                common_id=common_id,
                leafname="+renderjob,%s" % common_id,
                priority=outputspec.priority
            )
            workspec.create_uuid()
            workspec.verify_creation_data()
            work.append(workspec)
            stats_todo += 1
        
        stats = {
        "todo" : stats_todo,
        "done" : stats_done
        }
        return (work, stats)
            
            

    def get_all_work(self, selectors):
        work = []
        stats = {
            "todo" : 0,
            "done" : 0
        }
        root_album = SloeTree.inst().root_album
        logging.debug("get_all_work in %s" % root_album.name)
        for subtree, album, items in SloeTreeUtil.walk_items(root_album):
            logging.debug("%s In album: %s '%s' (%s)" % (album.uuid, album.name, album.title, album._location.replace("\\", "/")))
            outputspecs = SloeTreeUtil.get_parent_outputspecs(album)
            for outputspec in outputspecs:
                logging.debug("%s Scanning with OutputSpec: %s" % (outputspec.uuid, outputspec.name))

                for item in items:
                    if SloeTreeUtil.object_matches_selector(item, selectors):
                        (work_for_item, stats_for_item) = self.get_work_for_item(album, item, outputspec)
                        work += work_for_item
                        
                        for k in stats.keys():
                            stats[k] += stats_for_item[k]
                        
        sorted_work = reversed(sorted(work, key=lambda x: x.get("priority", 0.0)))
        logging.debug("get_all_work done")
        
        return (sorted_work, stats)


    def get_transfer_work_for_item(self, album, item, transferspec):
        work = []
        stats_todo = 0
        stats_done = 0
            
        common_id = "I=%s,T=%s" % (item.uuid, transferspec.uuid)
        found_item = SloeTreeUtil.find_remoteitem_by_spec({
            "common_id": common_id
        })
        if found_item is not None:
            stats_done += 1
        else:
            stats_todo += 1
            workspec = SloeTransferJob()
            workspec.set_values(
                name="transferitem %s" % datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%SZ'),
                common_id=common_id,
                leafname="+transferjob,%s" % common_id,
                priority=transferspec.priority,
                transfer_type = transferspec.transfer_type
            )
            workspec.create_uuid()
            workspec.verify_creation_data()
            work.append(workspec)
        
        stats = {
        "todo" : stats_todo,
        "done" : stats_done
        }
        return (work, stats)


    def get_all_transfer_work(self, selectors):
        work = []
        stats = {
            "todo" : 0,
            "done" : 0
        }
        root_album = SloeTree.inst().root_album
        logging.debug("get_all_transfer_work in %s" % root_album.name)
        for subtree, album, items in SloeTreeUtil.walk_items(root_album):
            logging.debug("%s In album: %s '%s' (%s)" % (album.uuid, album.name, album.title, album._location.replace("\\", "/")))
            transferspecs = SloeTreeUtil.get_parent_transferspecs(album)
            for transferspec in transferspecs:
                logging.debug("%s Scanning with TransferSpec: %s" % (transferspec.uuid, transferspec.name))

                combined_selectors = selectors + transferspec.selectors.split(",")
                for item in items:
                    if SloeTreeUtil.object_matches_selector(item, combined_selectors):
                        (work_for_item, stats_for_item) = self.get_transfer_work_for_item(album, item, transferspec)
                        work += work_for_item
                        
                        for k in stats.keys():
                            stats[k] += stats_for_item[k]
                        
        sorted_work = reversed(sorted(work, key=lambda x: x.get("priority", 0.0)))
        logging.debug("get_all_transfer_work done")
        
        return (sorted_work, stats)        
