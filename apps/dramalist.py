# -*- coding: utf-8 -*-
# @author AoBeom
# @create date 2017-12-22 09:45:54
# @modify date 2018-07-27 20:54:36
# @desc [字幕组更新信息]
import json
import multiprocessing
import re
import os
import sys
import time
from multiprocessing.dummy import Pool

import requests

try:
    from apps import redisMode
except BaseException:
    import redisMode

redis = redisMode.redisMode(crond=True)


class fixsub(object):
    def __init__(self):
        self.fixsub_host = "http://www.zimuxia.cn"

    def __request(self, url, params=None, timeout=30):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36"
        }
        if params:
            response = requests.get(
                url, headers=headers, params=params, timeout=timeout)
        else:
            response = requests.get(url, headers=headers, timeout=timeout)
        return response

    def fixPageInfo(self, page):
        fixsub_ajax = self.fixsub_host + "/wp-admin/admin-ajax.php"
        fixsub_type = "fix%e6%97%a5%e8%af%ad%e7%a4%be"
        params = {
            "page": page,
            "number": 8,
            "imgheight": 240,
            "columns": 4,
            "filterCats": ["68", "48", "66", "67", "70", "65", "71"],
            "filter_type": "include",
            "page_url": self.fixsub_host + "/%e6%88%91%e4%bb%ac%e7%9a%84%e4%bd%9c%e5%93%81",
            "require_nav": "false",
            "orderby": "menu_order",
            "order": "ASC",
            "action": "pexeto_get_portfolio_items",
            "cat": fixsub_type
        }
        response = self.__request(fixsub_ajax, params=params)
        fixsub_index = response.text
        fixsub_index_json = json.loads(fixsub_index)
        fixsub_page_info = fixsub_index_json["items"]
        return fixsub_page_info

    def fixSinglePageInfo(self, pageinfo):
        fixsub_page_info = pageinfo
        fixsub_single_page_info = {}
        fixsub_sp_rule = r'<a href="(.*?)" title="(.*?)">'
        fixsub_single = re.findall(
            fixsub_sp_rule, fixsub_page_info, re.S | re.M)
        for single in fixsub_single:
            fixsub_single_page_info[single[1]] = single[0]
        return fixsub_single_page_info

    def __geturl(self, url, tag):
        fixsub_url = url
        tag = tag
        count = 0
        url_infos = []
        if tag == "b_m_e_rule":
            for i in fixsub_url:
                episode = []
                baidu_url = i[0]
                magnet_url = i[1]
                ed2k_url = i[2]
                ep_rule = r'\.([SPE0-9]+)\.'
                result = re.findall(ep_rule, ed2k_url)
                if len(result) == 0:
                    try:
                        ep_num = re.findall(ep_rule, ed2k_url)[0]
                    except IndexError:
                        ep_num = "SP"
                else:
                    ep_num = result[0]
                episode.append(ep_num)
                episode.append(baidu_url)
                episode.append(magnet_url)
                episode.append(ed2k_url)
                url_infos.append(episode)
        elif tag == "b_m_rule":
            for i in fixsub_url:
                episode = []
                count = count + 1
                baidu_url = i[0]
                magnet_url = i[1]
                ep_rule = r'\.([SPE0-9]+)\.'
                result = re.findall(ep_rule, magnet_url)
                if len(result) == 0:
                    ep_num = str(count).zfill(2)
                else:
                    ep_num = result[0]
                episode.append(ep_num)
                episode.append(baidu_url)
                episode.append(magnet_url)
                url_infos.append(episode)
        elif tag == "b_rule":
            for i in fixsub_url:
                episode = []
                count = count + 1
                baidu_url = i[0]
                ep_num = str(count).zfill(2)
                episode.append(ep_num)
                episode.append(baidu_url)
                url_infos.append(episode)
        elif tag == "copyright":
            episode = []
            copyright = None
            episode.append(copyright)
            url_infos.append(episode)
        return url_infos

    def fixInfoGet(self, urls):
        fix_info = []
        fixsub_infos = urls
        # baidu,magnet,ed2k,_blank
        b_m_e_rule = re.compile(
            r'<a href="(http[s]?://pan.baidu.com.*?)".*?>.*?</a>.*?<a href="(magnet.*?)".*?>.*?</a>.*?<a href="(ed2k.*?)".*?>.*?</a>')
        # baidu,magnet,_blank
        b_m_rule = re.compile(
            r'<a href="(http[s]?://pan.baidu.com.*?)".*?>.*?</a>.*?<a href="(magnet.*?)".*?>.*?</a>')
        # baidu,_blank
        b_rule = re.compile(
            r'<a href="(http[s]?://pan.baidu.com.*?)".*?>.*?</a>')
        for title, url in fixsub_infos.items():
            fix_dict = {}
            info_list = []
            response = self.__request(url)
            fixsub_single = response.text
            b_m_e_url = b_m_e_rule.findall(fixsub_single)
            info_list.append(title)
            info_list.append(url)
            fix_dict["title"] = title
            fix_dict["url"] = url
            if len(b_m_e_url) == 0:
                b_m_url = b_m_rule.findall(fixsub_single)
                if len(b_m_url) == 0:
                    b_url = b_rule.findall(fixsub_single)
                    if len(b_url) == 0:
                        n_url = self.__geturl("", "copyright")
                        fix_dict["dlurls"] = n_url
                    else:
                        b_urls = self.__geturl(b_url, "b_rule")
                        fix_dict["dlurls"] = b_urls
                else:
                    b_m_urls = self.__geturl(b_m_url, "b_m_rule")
                    fix_dict["dlurls"] = b_m_urls
            else:
                b_m_e_urls = self.__geturl(b_m_e_url, "b_m_e_rule")
                fix_dict["dlurls"] = b_m_e_urls
            fix_info.append(fix_dict)
        return fix_info

    def fixPageNum(self):
        fixsub_jp_index = self.fixsub_host + \
            "/%E6%88%91%E4%BB%AC%E7%9A%84%E4%BD%9C%E5%93%81?cat=fix%E6%97%A5%E8%AF%AD%E7%A4%BE"
        fixsub_rule = r'<div class="pg-pagination">(.*?)</div>'
        response = self.__request(fixsub_jp_index)
        fixsub_index = response.text
        fixsub_pages_content = re.findall(
            fixsub_rule, fixsub_index, re.S | re.M)
        fixsub_pages_str = "".join(fixsub_pages_content)
        fixsub_pages = re.findall("data-page", fixsub_pages_str)
        return len(fixsub_pages)


class tvbtsub(object):
    def __init__(self):
        self.tvbt_host = "http://mytvbt.net"

    def __request(self, url, params=None, timeout=30):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36"
        }
        if params:
            response = requests.get(
                url, headers=headers, params=params, timeout=timeout)
        else:
            response = requests.get(url, headers=headers, timeout=timeout)
        return response

    def tvbtIndexInfo(self):
        tvbt_updates = []
        tvbt_index = self.tvbt_host + "/forumdisplay.php?fid=6"
        response = self.__request(tvbt_index)
        tvbt_index_info = response.text.encode("ISO-8859-1").decode("utf-8")
        tvbt_rule = '<a href="(.*)" style="font-weight: bold;color: #EE1B2E">(.*)</a>'
        tvbt_update_info = re.findall(tvbt_rule, tvbt_index_info)
        # top 2 remove
        tvbt_update_info.pop(0)
        tvbt_update_info.pop(0)
        for tvbt_update in tvbt_update_info:
            tvbt_info = []
            tvbt_uptime = tvbt_update[1][1:6].replace(".", "")
            tvbt_mainurl = self.tvbt_host + "/" + tvbt_update[0]
            tvbt_title = tvbt_update[1][6:]
            tvbt_info.append(tvbt_uptime)
            tvbt_info.append(tvbt_mainurl)
            tvbt_info.append(tvbt_title)
            tvbt_updates.append(tvbt_info)
        return tvbt_updates

    def tvbtGetUrl(self, updateinfo):
        tvbt_updates = updateinfo
        tvbt_infos = []
        for updates in tvbt_updates:
            tvbt_dict = {}
            count = 0
            tvbt_title_rule = r'\](.*?)\['
            # tvbt_dl_rule = r'<a href="(http[s]?://pan.baidu.com.*?)" target="_blank">.*?</a>.*?([0-9a-zA-Z]+).*?<'
            tvbt_dl_rule1 = r'<a href="(http[s]?://pan.baidu.com.*?)" target="_blank">.*?</a>.*?([0-9a-zA-Z]+).*?<'
            tvbt_dl_rule2 = r'<a href="(http[s]?://pan.baidu.com.*?)" target="_blank">.*?</a> <br />.*?([0-9a-zA-Z]+).*?>'
            tvbt_uptime = updates[0]
            tvbt_url = updates[1]
            tvbt_title = updates[2]
            tvbt_title_main = re.findall(tvbt_title_rule, tvbt_title)
            for title in tvbt_title_main:
                if title:
                    tvbt_title = title.split("-")[-1].strip()
            tvbt_dict["date"] = tvbt_uptime
            tvbt_dict["url"] = tvbt_url
            tvbt_dict["title"] = tvbt_title
            response = self.__request(tvbt_url)
            tvbt_single_index = response.text.encode(
                "ISO-8859-1").decode("utf-8")
            tvbt_single_info1 = re.findall(tvbt_dl_rule1, tvbt_single_index, re.S | re.M)
            tvbt_single_info2 = re.findall(tvbt_dl_rule2, tvbt_single_index, re.S | re.M)
            tvbt_single_info1 = [i for i in tvbt_single_info1 if i[1] != "br"]
            tvbt_single_info = tvbt_single_info1 + tvbt_single_info2
            # if len(tvbt_single_info) == 0:
            #     tvbt_dl_rule = r'<a href="(http[s]?://pan.baidu.com.*?)" target="_blank">.*?</a>'
            #     tvbt_dl_pass = u'.*?提取码：([0-9a-zA-Z]+).*?<'
            #     tvbt_single_url = re.findall(tvbt_dl_rule, tvbt_single_index)
            #     tvbt_single_dl = re.findall(tvbt_dl_pass, tvbt_single_index)
            #     tvbt_single_info = [tvbt_single_url + tvbt_single_dl]
            tvbt_dl_urls = []
            for info in tvbt_single_info:
                dl_urls = []
                count = count + 1
                ep_num = str(count).zfill(2)
                baidu_url = info[0]
                baidu_passwd = info[1]
                dl_urls.append(ep_num)
                dl_urls.append(baidu_url)
                dl_urls.append(baidu_passwd)
                tvbt_dl_urls.append(dl_urls)
                tvbt_dict["dlurls"] = tvbt_dl_urls
            tvbt_infos.append(tvbt_dict)
        return tvbt_infos


class subpig_rbl(object):
    def __init__(self):
        self.subpig_host = "http://www.zzrbl.com"

    def __request(self, url, params=None, timeout=30):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36"
        }
        if params:
            try:
                response = requests.get(
                    url, headers=headers, params=params, timeout=timeout)
            except BaseException as e:
                sys.exit(e)
        else:
            try:
                response = requests.get(url, headers=headers, timeout=timeout)
            except BaseException as e:
                sys.exit(e)
        return response

    def subpigIndexInfo(self):
        # first and second page
        pages = 2
        subpig_index_info = []
        for i in range(1, pages + 1):
            subpig_page = self.subpig_host + \
                "/wordpress/?cat=11&page=1&paged={}".format(i)
            subpig_rule = r'<li><a href="(.*?)" title="(.*?)">.*?</a>.*?</li>'
            response = self.__request(subpig_page)
            subpig_index = response.text
            subpig_content = re.findall(subpig_rule, subpig_index, re.S | re.M)
            for sub_cont in subpig_content:
                subpig_info_dict = {}
                subpig_title_origin = sub_cont[1]
                subpig_rule_utime = r'[0-9\/]+'
                subpig_utime = re.findall(
                    subpig_rule_utime, subpig_title_origin.split("]")[-1])
                subpig_utime = ''.join(subpig_utime)
                subpig_rule_title = r'\[(.*?)\]'
                subpig_title = re.findall(
                    subpig_rule_title, subpig_title_origin)
                subpig_info_dict["url"] = sub_cont[0]
                subpig_info_dict["date"] = subpig_utime
                subpig_info_dict["title"] = subpig_title[1]
                subpig_index_info.append(subpig_info_dict)
        return subpig_index_info

    def subpigGetUrl(self, infos):
        subpig_drule = r'<p>.*?<a href="(http[s]?://pan.baidu.com.*?)".*?>.*?</a>.*?([0-9a-zA-Z]+).*?</p>'
        murl = infos["url"]
        response = self.__request(murl)
        subpig_main = response.text
        subpig_durls = re.findall(subpig_drule, subpig_main, re.S | re.M)
        if not subpig_durls:
            subpig_drule = r'>.*?(http[s]?://pan.baidu.com.*?).*?([0-9a-zA-Z]+).*?<'
            subpig_durls = re.findall(subpig_drule, subpig_main, re.S | re.M)
        for durl in subpig_durls:
            subpig_dlinfo = []
            subpig_purl = durl[0]
            subpig_pass = durl[1]
            subpig_dlinfo.append(subpig_purl)
            subpig_dlinfo.append(subpig_pass)
            infos["dlurls"] = subpig_dlinfo
        return infos


def main():
    tvbt_key = "drama:tvbt"
    t = tvbtsub()
    tvbt_update_info = t.tvbtIndexInfo()
    tvbt_urls = t.tvbtGetUrl(tvbt_update_info)
    times = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    redis.redisSave("drama:utime", times)
    redis.redisSave(tvbt_key, tvbt_urls)

    subpig_key = "drama:subpig"
    p = subpig_rbl()
    index_subpig = p.subpigIndexInfo()
    pool = Pool(10)
    subpig_urls = pool.map(p.subpigGetUrl, index_subpig)
    pool.close()
    pool.join
    redis.redisSave(subpig_key, subpig_urls)

    pages = 1
    fix_key = "drama:fixsub"
    f = fixsub()
    # pages = f.fixPageNum()
    for page in range(1, pages + 1):
        fix_page_info = f.fixPageInfo(page)
        fix_single_page = f.fixSinglePageInfo(fix_page_info)
        fix_dl_urls = f.fixInfoGet(fix_single_page)
    redis.redisSave(fix_key, fix_dl_urls)


def tvbt_process(name):
    print("Run {} [{}]...".format(name, os.getpid()))
    tvbt_key = "drama:tvbt"
    t = tvbtsub()
    tvbt_update_info = t.tvbtIndexInfo()
    tvbt_urls = t.tvbtGetUrl(tvbt_update_info)
    redis.redisSave(tvbt_key, tvbt_urls)
    print("{} [{}] done".format(name, os.getpid()))


def subpig_process(name):
    print("Run {} [{}]...".format(name, os.getpid()))
    subpig_key = "drama:subpig"
    p = subpig_rbl()
    subpig_update_info = p.subpigIndexInfo()
    if subpig_update_info:
        pool = Pool(4)
        subpig_urls = pool.map(p.subpigGetUrl, subpig_update_info)
        pool.close()
        pool.join
        redis.redisSave(subpig_key, subpig_urls)
    else:
        print("No data")
    print("{} [{}] done".format(name, os.getpid()))


def fixsub_process(name):
    print("Run {} [{}]...".format(name, os.getpid()))
    pages = 1
    fix_key = "drama:fixsub"
    f = fixsub()
    # pages = f.fixPageNum()
    for page in range(1, pages + 1):
        fix_page_info = f.fixPageInfo(page)
        fix_single_page = f.fixSinglePageInfo(fix_page_info)
        fix_dl_urls = f.fixInfoGet(fix_single_page)
    redis.redisSave(fix_key, fix_dl_urls)
    print("{} [{}] done".format(name, os.getpid()))


def main2():
    times = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    redis.redisSave("drama:utime", times)

    pool = multiprocessing.Pool()
    tasks = {
        "TVBT": tvbt_process,
        "FIXSUB": fixsub_process,
        "SUBPIG": subpig_process
    }
    print("Main process [{}] start".format(os.getpid()))
    for name, func in tasks.items():
        pool.apply_async(func, args=(name, )).get(30)
    print("Waiting for all subprocesses done...")
    pool.close()
    pool.join()
    print("All process done")


if __name__ == "__main__":
    main2()
