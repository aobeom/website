#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author AoBeom
# @create date 2017-12-22 09:49:14
# @modify date 2020-01-21 17:17:08
# @desc [HLS直播地址获取]
import json
import re
import time

import requests


class HLSPlayList(object):
    def __init__(self):
        self.headers = {
            "User-Agent":
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36",
        }
        self.session = requests.Session()

    def urlCheck(self, url):
        host_rule = re.compile(
            r'https?://(.*showroom-live\.com/.*|live\.line\.me/.*)')
        if host_rule.match(url):
            site = url.split("/")[2]
            return site, url
        else:
            return None

    def urlRouter(self, urltype):
        if urltype:
            site = urltype[0]
            url = urltype[1]
            if site == "www.showroom-live.com":
                url = self.__showroom(url)
            else:
                url = self.__linelive(url)
            return url
        else:
            return None

    def __linelive(self, url):
        channel = url.split("channels")[-1]
        url = "https://live-api.line-apps.com/app/v2/channel" + channel
        res = self.session.get(url, headers=self.headers)
        jsonData = json.loads(res.text)
        liveHLSURLs = jsonData["liveHLSURLs"]
        url = liveHLSURLs["720"]
        return url

    def __showroom(self, url):
        res = self.session.get(url, headers=self.headers)
        idRule = r'href=\"\/room\/profile\?room_id=([0-9]+)\"'
        room_id = re.findall(idRule, res.text, re.S | re.M)
        if room_id:
            api_url = "https://www.showroom-live.com/api/live/streaming_url"
            params = {
                "room_id": room_id,
                "ignore_low_stream": 1,
                "_": int(time.time()*1000)
            }
            res = self.session.get(api_url, params=params, headers=self.headers)
            jsonData = json.loads(res.text)
            urls = jsonData["streaming_url_list"]
            for u in urls:
                if u["type"] == "hls":
                    return u["url"]
            return None
        else:
            return None
