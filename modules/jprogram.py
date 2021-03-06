#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author AoBeom
# @create date 2017-12-22 09:47:38
# @modify date 2018-03-07 13:51:23
# @desc [雅虎节目表关键词搜索]

import re

import requests


class yahooTV(object):
    def __init__(self):
        self.host = "https://tv.yahoo.co.jp"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded"
        }

    def tvInfos(self, keyword, code=23):
        apihost = self.host + "/search/category/"
        params = {
            "q": keyword,
            "a": code,
            "oa": 1,
            "tv": 1,
            "bsd": 1
        }
        response = requests.post(apihost, headers=self.headers, data=params)
        tv_index = response.text
        tv_url = response.url
        date_time = self.__tvLeftInfo(tv_index)
        url_title_station = self.__tvRightInfo(tv_index)
        tv_all_info = zip(date_time[0], date_time[1],
                          url_title_station[0], url_title_station[1], url_title_station[2])
        if tv_all_info:
            tv_infos = []
            for t in tv_all_info:
                tv_dict = {}
                tv_dict["date"] = t[0]
                tv_dict["time"] = t[1]
                tv_dict["url"] = t[2]
                tv_dict["title"] = t[3]
                tv_dict["station"] = t[4]
                tv_infos.append(tv_dict)
            return [tv_infos, tv_url]

    def __tvLeftInfo(self, index):
        tv_index = index
        tv_body_l_rule = r'<div class="leftarea">(.*?)</div>'
        tv_result_l = re.findall(tv_body_l_rule, tv_index, re.S | re.M)
        dates = []
        times = []
        for tv_l in tv_result_l:
            tv_target_rule = r'<em>(.*?)</em>.*?<em>(.*?)</em>'
            date_time = re.findall(tv_target_rule, tv_l, re.S | re.M)
            for dt in date_time:
                dates.append(dt[0])
                times.append(dt[1])
        return dates, times

    def __tvRightInfo(self, index):
        tv_index = index
        tv_body_r_rule = r'<div class="rightarea">(.*?)</div>'
        tv_result_r = re.findall(tv_body_r_rule, tv_index, re.S | re.M)
        urls = []
        titles = []
        station = []
        for tv_r in tv_result_r:
            tv_target_rule = r'<a href="(.*?)">(.*?)</a></p>.*?<span class="pr35">(.*?)</span>.*?'
            url_title_station = re.findall(tv_target_rule, tv_r, re.S | re.M)
            for uts in url_title_station:
                urls.append(self.host + uts[0])
                titles.append(uts[1])
                station.append(uts[2])
        return urls, titles, station
