#!/usr/bin/python

import cPickle
import logging
import os
import pprint
import time

import sloelib

from sloeyoutubeitem import SloeYouTubeItem

class SloeYouTubeTree:
  IDMAP_CACHE_FILENAME = "youtubetree_idmap_cache.pickle"
  IDMAP_CACHE_VALID_FILENAME = "youtubetree_idmap_cache.valid"

  def __init__(self, session):
    self.session = session
    self.item_list = {}
    self.id_map = {}

  def _save_cache(self):
    logging.info("Saving ID map cache from %s" % self.IDMAP_CACHE_FILENAME)

    if os.path.exists(self.IDMAP_CACHE_VALID_FILENAME):
      os.unlink(self.IDMAP_CACHE_VALID_FILENAME)

    with open(self.IDMAP_CACHE_FILENAME, "wb") as file:
      if file:
        cPickle.dump(self.id_map, file)

    with open(self.IDMAP_CACHE_VALID_FILENAME, "wb") as file:
      file.write("Cache validated %s" % time.asctime())


  def _load_cache(self):
    if not os.path.exists(self.IDMAP_CACHE_VALID_FILENAME):
      if os.path.exists(self.IDMAP_CACHE_FILENAME):
        logging.warn("Ignoring cache file %s as not valid" % self.IDMAP_CACHE_FILENAME)
    else:
      logging.info("Loading ID map cache from %s" % self.IDMAP_CACHE_FILENAME)
      file = open(self.IDMAP_CACHE_FILENAME, "rb")
      if file:
        id_map = cPickle.load(file)
        self.id_map = id_map

  def _get_channels(self):
    channels = self.session().channels()
    channel_list = channels.list(
      mine=True,
      part="contentDetails"
    )
    return channel_list.execute()["items"]

  def read(self):
    self._load_cache()

    updated = True

    for channel in self._get_channels():
      uploads_list_id = channel["contentDetails"]["relatedPlaylists"]["uploads"]

      playlistitems_list_request = self.session().playlistItems().list(
        playlistId=uploads_list_id,
        part="snippet",
        maxResults=50
      )

      while playlistitems_list_request:
        playlistitems_list_response = playlistitems_list_request.execute()

        video_ids = []
        video_specs = []
        for playlist_item in playlistitems_list_response["items"]:
          video_id = playlist_item["snippet"]["resourceId"]["videoId"]

          video_spec = playlist_item["snippet"]
          video_spec[u"sloemodified"] = False
          video_ids.append(video_id)
          video_specs.append(video_spec)

        videolistitems_list_request = self.session().videos().list(
          part=" id, snippet, contentDetails, fileDetails,liveStreamingDetails,player,processingDetails,recordingDetails,statistics,status,suggestions,topicDetails",
          id = u",".join(video_ids)
          )

        videolistitems_list_response = videolistitems_list_request.execute()

        for i, v in enumerate(videolistitems_list_response["items"]):
          video_specs[i][u"sloevideo"] = v

        for i, video_id in enumerate(video_ids):
          self.item_list[video_id] = SloeYouTubeItem(video_specs[i])
          self.item_list[video_id].update_video_description("Sloecoach test video")
          self.item_list[video_id].set_sloeid_tag("01234567890")

        playlistitems_list_request = self.session().playlistItems().list_next(
          playlistitems_list_request, playlistitems_list_response)

    if updated:
      self._save_cache()


  def write(self):
    for item_id, item in self.item_list.iteritems():
      if item.get("sloemodified"):
        logging.info("Item %s is modified - updating" % item_id)
        self.update_item(item)


  def update_item(self, item):
    sloevideo = item.get("sloevideo")
    videos_update_request = self.session().videos().update(
      part="snippet",
      body={
        "id":sloevideo["id"],
        "snippet":sloevideo["snippet"]
      })
    videos_update_request.execute()


  def __repr__(self):
    return pprint.pformat(self.item_list)


