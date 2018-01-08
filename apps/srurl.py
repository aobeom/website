#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author AoBeom
# @create date 2017-12-22 09:49:14
# @modify date 2018-01-08 12:53:01
# @desc [showroom-live直播地址获取]

import re

import requests

from apps import statusHandler


class SRPlayList(object):
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36",
        }

    def getUrl(self, url):
        response = requests.get(url, headers=self.headers)
        sr_index = response.text
        sr_rule = r'https://[0-9a-z\.\:\-]+/liveedge/[0-9a-z]+/playlist.m3u8'
        sr_playlists = re.findall(sr_rule, sr_index)
        sr_owner = url.split("/")[-1]
        if len(sr_playlists) != 0:
            sr_playlist = sr_playlists[0]
            datas = statusHandler.handler(0, sr_playlist, sr_owner)
        else:
            datas = statusHandler.handler(1, None, sr_owner, message="Not yet started")
        return datas
