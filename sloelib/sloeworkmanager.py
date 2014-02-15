
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
from sloetreeutil import SloeTreeUtil


class SloeWorkManager(object):
    def __init__(self, tree):
        self.tree = tree    


    def get_work_for_item(self, album, item, outputspec):
        work = []
        add_workspec = False
        glob_include = outputspec.get("glob_include", None)
        if fnmatch.fnmatch(item.leafname, glob_include):
            add_workspec = True
            
        if add_workspec:
            common_id = "O=%s,I=%s" % (outputspec.uuid, item.uuid)
            workspec = SloeRenderJob()
            workspec.set_values(
                common_id=common_id,
                leafname="+renderjob,%s" % common_id,       
                uuid=str(uuid.uuid4())
            )
            work.append(workspec)
        
        return work
            
            

    def get_all_work(self, tree):
        work = []
        root_album = self.tree.get_root_album()
        logging.debug("get_all_work in %s" % root_album.name)
        for subtree, album, items in SloeTreeUtil.walk_items(root_album):
            logging.debug("%s In album: %s '%s' (%s)" % (album.uuid, album.name, album.title, album._location.replace("\\", "/")))
            outputspecs = SloeTreeUtil.get_parent_outputspecs(album)
            for outputspec in outputspecs:
                logging.debug("%s Scanning with OutputSpec: %s" % (outputspec.uuid, outputspec.name))

                for item in items:
                    work += self.get_work_for_item(album, item, outputspec)                    
            
        logging.debug("get_all_work done")
        return work


