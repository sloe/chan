
import logging
import os
import sys
from pprint import pprint, pformat

from sloeconfig import SloeConfig
from sloeerror import SloeError
from sloetreenode import SloeTreeNode


class SloeItem(SloeTreeNode):
    MANDATORY_ELEMENTS = {
        "leafname": "Leafname (filename) of the item",
        "name": "Primary name of the item"
    }
    MANDATORY_ELEMENTS.update(SloeTreeNode.MANDATORY_ELEMENTS)
    OPTIONAL_ELEMENTS = {
        "common_id": "IDs of related items in common ID format",
        "audio_bit_rate": "Audio bit rate in (bits per second)",
        "audio_channels": "Number of audio channels",
        "audio_codec_name": "Name of audio codec",
        "audio_duration": "Duration of audio track(s) (seconds)",
        "audio_nb_frames": "Number of audio frames",
        "audio_sample_fmt": "Audio sample format",
        "audio_sample_rate": "Audio sample rate in (samples per second)",
        "video_avg_frame_rate": "Video frame rate (frames per second)",
        "video_bit_rate": "Video bit rate (bits per second)",
        "video_codec_name": "Name of video codec",
        "video_duration": "Duration of video track(s) (seconds)",
        "video_format_long_name": "Name of video format, long",
        "video_format_name": "Name of video format, short",
        "video_height": "Height of video (pixels)",
        "video_level": "Level of video codec",
        "video_nb_frames": "Number of video frames",
        "video_pix_fmt": "Video pixel format",
        "video_size": "Video size (bytes)",
        "video_width": "Width of video (pixels)"
    }
    OPTIONAL_ELEMENTS.update(SloeTreeNode.OPTIONAL_ELEMENTS)

    def __init__(self):
        SloeTreeNode.__init__(self, "item", "01")


    def create_new(self, existing_item, spec):
        if existing_item:
            # Preserve information in existing item
            for k, v in existing_item._d.iteritems():
                if not k.startswith("auto_"):
                    if k in spec and v != spec[k]:
                        logging.warn("Mismatched original item: element %s new %s !=  old %s" % (
                            k, v, spec[k]))

                    self._d[k] = v
            self._d.update(spec)

        else:
            self._d.update(spec)
            if "uuid" not in self._d:
                self.create_uuid()

        self.verify_creation_data()
        self.add_to_library()


    @classmethod
    def new_from_ini_file(cls, ini_filepath, error_info):
        item = SloeItem()
        item.create_from_ini_file(ini_filepath, error_info)
        return item


    def get_file_dir(self):
        root_dir = SloeConfig.inst().get_global("treeroot")
        return os.path.join(root_dir, self._d["_primacy"], self._d["_worth"], self._d["_subtree"])


    def get_file_path(self):
        return os.path.join(self.get_file_dir(), self._d["leafname"])


    def get_ini_filepath(self):
        treepath = os.path.dirname(self.get_file_path())
        return os.path.join(treepath, self.get_ini_leafname());


    def get_file_url_subpath(self):
        return "{0}/{1}".format(self._d["_subtree"], self._d["leafname"])


    def dump(self):
        return pformat(self._d)


    def __repr__(self):
        return "|Item|%s" % pformat(self._d)



SloeTreeNode.add_factory("ITEM", SloeItem)