#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author AoBeom
# @create date 2017-12-22 09:49:14
# @modify date 2018-01-05 10:52:31
# @desc [showroom-live直播地址获取]

import re

import requests


class SRPlayList(object):
    def __init__(self):
        pass

    def getUrl(self, url):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36",
        }
        index = requests.get(url, headers=headers)
        index_code = index.text
        rule = re.compile(
            r'https://[0-9a-z\.\:\-]+/liveedge/[0-9a-z]+/playlist.m3u8')
        try:
            playlist_results = rule.findall(index_code)
            playlist = playlist_results[0]
        except BaseException:
            print("Room: {}".format(url))
            return None
        return playlist
