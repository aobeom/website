# -*- coding: utf-8 -*-
# @author AoBeom
# @create date 2017-12-22 09:45:25
# @modify date 2018-01-05 10:52:34
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
    datas = {}
    if "showroom-live" in url:
        delType = "m3u8"
        redis_key = "{}:{}".format("showroom", url)
        redisSR = r.redisCheck(redis_key, subkey=True)
        if redisSR:
            hlsurl = redisSR
            datas["status"] = 0
            datas["type"] = delType
            datas["urls"] = hlsurl
        else:
            sr = srurl.SRPlayList()
            hlsurl = sr.getUrl(url)
            if hlsurl:
                datas["status"] = 0
                datas["type"] = delType
                datas["urls"] = hlsurl
                r.redisSave(redis_key, hlsurl, ex=300, subkey=True)
            else:
                datas["status"] = 1
    else:
        delType = "picture"
        p = picdown.picdown()
        urldict = p.urlCheck(url)
        sitename = urldict["site"]
        siteurl = urldict["url"]
        redis_key = "{}:{}".format(sitename, siteurl)
        redisUrls = r.redisCheck(redis_key, subkey=True)
        if redisUrls:
            urls = redisUrls
            urls = r.redisList(urls)
            datas["status"] = 0
            datas["type"] = delType
            datas["urls"] = urls
        else:
            imgurl = p.photoUrlGet(urldict)
            if imgurl:
                datas["status"] = 0
                datas["type"] = delType
                datas["urls"] = imgurl
                r.redisSave(redis_key, imgurl, ex=259200, subkey=True)
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
        redis_key = "drama:{}".format(sitename)
        datas["type"] = sitename
        redisResult = r.redisCheck(redis_key)
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
                r.redisSave(redis_key, dramaContent)
            else:
                datas["status"] = 1
    if id_type["id"] == "subpig":
        sitename = "subpig"
        redis_key = "drama:{}".format(sitename)
        datas["type"] = sitename
        redisResult = r.redisCheck(redis_key)
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
                r.redisSave(redis_key, dramaContent)
            else:
                datas["status"] = 1
    if id_type["id"] == "fixsub":
        sitename = "fixsub"
        redis_key = "drama:{}".format(sitename)
        datas["type"] = sitename
        redisResult = r.redisCheck(redis_key)
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
                r.redisSave(redis_key, dramaContent)
            else:
                datas["status"] = 1
    return jsonify(datas)


@app.route('/programget/', methods=['POST'])
def program_request():
    kw_json = request.get_json()
    keyword = kw_json["kw"].encode("utf-8")
    reids_key = "program:{}".format(keyword)
    r = redisMode.redisMode()
    datas = {}
    redisKeyword = r.redisCheck(reids_key, subkey=True)
    if redisKeyword:
        rediskeyword = redisKeyword
        rediskeyword = r.redisList(rediskeyword)
        datas["status"] = 0
        try:
            keyword = str(keyword, encoding="utf-8")
        except TypeError:
            keyword = keyword
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
            r.redisSave(reids_key, tvdatas, ex=14400, subkey=True)
        else:
            datas["status"] = 1
    return jsonify(datas)


@app.route('/utime/', methods=['GET'])
def drama_utime():
    r = redisMode.redisMode()
    utime = r.conn.get("drama:utime")
    try:
        utime = str(utime, encoding="utf-8")
    except TypeError:
        utime = utime
    if utime:
        utime_timestamp = int(time.mktime(
            time.strptime(str(utime), '%Y-%m-%d %H:%M:%S')))
        ntime_timestamp = int(time.time())
        ltime_timestamp = utime_timestamp + 14400
        countdown_sec = ltime_timestamp - ntime_timestamp
        now = {"date": utime, "countdown": countdown_sec}
    else:
        now = {"date": None}
    return jsonify(now)
