#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author AoBeom
# @create date 2017-12-22 09:49:14
# @modify date 2018-03-24 13:38:43
# @desc [HLS直播地址获取]

import re

import requests


class HLSPlayList(object):
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36",
        }

    def urlCheck(self, url):
        host_rule = re.compile(r'https?://.*showroom-live\.com/.*|live\.line\.me/.*')
        if host_rule.match(url):
            site = url.split("/")[2]
            return site, url
        else:
            return None

    def urlRouter(self, urltype):
        rules = {
            "www.showroom-live.com": r'https://[0-9a-z\.\:\-]+/liveedge/[0-9a-z]+/playlist.m3u8',
            "live.line.me": r'https://lss.line-scdn.net/p/live/[\S]+/[0-9]+/chunklist.m3u8'
        }
        if urltype:
            site = urltype[0]
            url = urltype[1]
            rule = rules[site]
            m3u8_url = self.__getUrl(url, rule)
            return m3u8_url
        else:
            return None

    def __getUrl(self, url, rule):
        response = requests.get(url, headers=self.headers)
        m3u8_index = response.text
        m3u8_playlists = re.findall(rule, m3u8_index, re.S | re.M)
        if len(m3u8_playlists) != 0:
            sr_playlist = m3u8_playlists[0]
            return sr_playlist
        else:
            return None
