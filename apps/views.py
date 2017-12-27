# -*- coding: utf-8 -*-
# @author AoBeom
# @create date 2017-12-22 09:45:25
# @modify date 2017-12-25 11:19:45
# @desc [Flask view main]

import time
from multiprocessing.dummy import Pool

from flask import jsonify, render_template, request

from apps import app, dramalist, jprogram, picdown, redisMode, srurl


@app.route('/')
@app.route('/picture')
def index():
    return render_template("picdown_index.html")


@app.route('/drama')
def dramaindex():
    return render_template("drama_index.html")


@app.route('/program')
def programindex():
    return render_template("program_index.html")


@app.route('/picdown/', methods=['POST'])
def pic_request():
    url_json = request.get_json()
    url = url_json["url"]
    r = redisMode.redisMode()
    p = picdown.picdown()
    redisUrls = r.redisCheck(url, md5value=True)
    datas = {}
    if redisUrls:
        if "showroom-live" in url:
            delType = "m3u8"
            redisurl = redisUrls
            datas["urls"] = redisurl
        else:
            redisurl = redisUrls
            delType = "picture"
            redisurl = r.redisList(redisurl)
            datas["urls"] = redisurl
        datas["status"] = 0
        datas["type"] = delType
    else:
        if "showroom-live" in url:
            delType = "m3u8"
            datas["type"] = delType
            sr = srurl.SRPlayList()
            hlsurl = sr.getUrl(url)
            if hlsurl:
                datas["status"] = 0
                datas["urls"] = hlsurl
                r.redisSave(url, hlsurl, ex=300, md5value=True)
            else:
                datas["status"] = 1
        else:
            delType = "picture"
            datas["type"] = delType
            urldict = p.urlCheck(url)
            imgurl = p.photoUrlGet(urldict)
            if imgurl:
                datas["status"] = 0
                datas["urls"] = imgurl
                r.redisSave(url, imgurl, ex=259200, md5value=True)
            else:
                datas["status"] = 1
    return jsonify(datas)


@app.route('/dramaget/', methods=['POST'])
def drama_request():
    id_type = request.get_json()
    r = redisMode.redisMode()
    datas = {}
    if id_type["id"] == "tvbt":
        sitename = "tvbt"
        datas["type"] = sitename
        redisResult = r.redisCheck(sitename)
        homepage = "http://mytvbt.net/forumdisplay.php?fid=6"
        datas["homepage"] = homepage
        if redisResult:
            redisResult = r.redisList(redisResult)
            dramaContent = redisResult
            datas["status"] = 0
            datas["datas"] = dramaContent
        else:
            t = dramalist.tvbtsub()
            tvbt_update_info = t.tvbtIndexInfo()
            dramaContent = t.tvbtGetUrl(tvbt_update_info)
            if dramaContent:
                datas["status"] = 0
                datas["datas"] = dramaContent
                r.redisSave(sitename, dramaContent)
            else:
                datas["status"] = 1
    if id_type["id"] == "subpig":
        sitename = "subpig"
        datas["type"] = sitename
        redisResult = r.redisCheck(sitename)
        homepage = "http://www.jpdrama.cn/forum.php?mod=forumdisplay&fid=306&page=1"
        datas["homepage"] = homepage
        if redisResult:
            redisResult = r.redisList(redisResult)
            dramaContent = redisResult
            datas["status"] = 0
            datas["datas"] = dramaContent
        else:
            p = dramalist.subpig()
            subpig_update_info = p.subpigIndexInfo()
            pool = Pool(10)
            dramaContent = pool.map(p.subpigGetUrl, subpig_update_info)
            pool.close()
            pool.join
            if dramaContent:
                datas["status"] = 0
                datas["datas"] = dramaContent
                r.redisSave(sitename, dramaContent)
            else:
                datas["status"] = 1
    if id_type["id"] == "fixsub":
        sitename = "fixsub"
        datas["type"] = sitename
        redisResult = r.redisCheck(sitename)
        homepage = "http://www.zimuxia.cn/%E6%88%91%E4%BB%AC%E7%9A%84%E4%BD%9C%E5%93%81?cat=fix%E6%97%A5%E8%AF%AD%E7%A4%BE"
        datas["homepage"] = homepage
        if redisResult:
            redisResult = r.redisList(redisResult)
            dramaContent = redisResult
            datas["status"] = 0
            datas["datas"] = dramaContent
        else:
            f = dramalist.fixsub()
            pages = 1
            for page in range(1, pages + 1):
                fix_page_info = f.fixPageInfo(page)
                fix_single_page = f.fixSinglePageInfo(fix_page_info)
                dramaContent = f.fixInfoGet(fix_single_page)
            if dramaContent:
                datas["status"] = 0
                datas["datas"] = dramaContent
                r.redisSave(sitename, dramaContent)
            else:
                datas["status"] = 1
    return jsonify(datas)


@app.route('/programget/', methods=['POST'])
def program_request():
    kw_json = request.get_json()
    keyword = kw_json["kw"]
    r = redisMode.redisMode()
    datas = {}
    redisKeyword = r.redisCheck(keyword, md5value=True)
    if redisKeyword:
        rediskeyword = redisKeyword
        rediskeyword = r.redisList(rediskeyword)
        datas["status"] = 0
        datas["url"] = keyword
        datas["datas"] = rediskeyword
    else:
        y = jprogram.yahooTV()
        tvinfo = y.tvInfos(keyword)
        tvurl = tvinfo[0]
        tvdatas = tvinfo[1]
        if tvdatas:
            datas["status"] = 0
            datas["url"] = tvurl
            datas["datas"] = tvdatas
            r.redisSave(keyword, tvdatas, ex=14400, md5value=True)
        else:
            datas["status"] = 1
    return jsonify(datas)


@app.route('/utime/', methods=['GET'])
def drama_utime():
    r = redisMode.redisMode()
    utime = r.conn.get("utime")
    if utime:
        utime_timestamp = int(time.mktime(
            time.strptime(utime, '%Y-%m-%d %H:%M:%S')))
        ntime_timestamp = int(time.time())
        ltime_timestamp = utime_timestamp + 14400
        countdown_sec = ltime_timestamp - ntime_timestamp
        now = {"date": utime, "countdown": countdown_sec}
    else:
        now = {"date": None}
    return jsonify(now)
