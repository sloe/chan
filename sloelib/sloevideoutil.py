

import json
import logging
import os
from pprint import pprint, pformat
import subprocess

from sloeconfig import SloeConfig
from sloeerror import SloeError

class SloeVideoUtil(object):
    
    @classmethod
    def detect_video_params(cls, filepath):
        output = {}
        command = [
            SloeConfig.get_global("ffprobe"),
            filepath,
            "-print_format", "json", "-show_format", "-show_streams"]

        p = subprocess.Popen(command, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        (json_out, stderr) = p.communicate()
        if p.returncode != 0:
            logging.error("ffprobe failed (rc=%d)\n%s" % (p.returncode, stderr))
            raise sloelib.SloeError("ffprobe failed (rc-%d)" % p.returncode)
        ffinfo = json.loads(json_out)
        for stream in ffinfo["streams"]:
            if stream["codec_type"] == "video":
                for name in ("codec_name", "width", "height", "pix_fmt", "level", "avg_frame_rate", "duration", "nb_frames"):
                    if name in stream:
                        output["auto_video_" + name] = stream[name]
            elif stream["codec_type"] == "audio":
                for name in ("bit_rate", "codec_name", "sample_fmt", "sample_rate", "channels", "duration", "nb_frames"):
                    if name in stream:
                        output["auto_audio_" + name] = stream[name]
            else:
                handler_name = stream.get("tags", {}).get("handler_name", "")
                if handler_name == "Timed Metadata Handler":
                    logging.debug("Ignoring Timed Metadata Handler stream")
                else:
                    logging.error("Ignoring unknown stream %s" % pformat(stream))
        for name in ("format_name", "format_long_name", "size", "bit_rate"):
            if name in ffinfo["format"]:
                output["auto_video_" + name] = ffinfo["format"][name]
                       
        return output
                   