# -*- coding: utf-8 -*-
# @author AoBeom
# @create date 2017-12-22 09:45:25
# @modify date 2018-01-09 10:18:59
# @desc [Flask view main]

import time
from multiprocessing.dummy import Pool

from flask import jsonify, render_template, request

from apps import app, dramalist, jprogram, picdown, redisMode, srurl, statusHandler, limitrate, dlcore

API_VERSION = "/v1"
API_PICDOWN = API_VERSION + "/api/picdown"
API_DRAMA = API_VERSION + "/api/dramaget"
API_PROGRAM = API_VERSION + "/api/programget"
API_UTIME = API_VERSION + "/api/utime"
API_ST = API_VERSION + "/api/stinfo"
API_STDL = API_VERSION + "/api/stdl"


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


@app.route('/stchannel')
def stindex():
    return render_template("st_index.html")


@app.route(API_PICDOWN, methods=['GET'])
def pic_request():
    url = request.args.get("url")
    r = redisMode.redisMode()
    if url:
        clientip = request.remote_addr
        limitinfo = limitrate.limitIP(clientip)
        if limitinfo is None:
            if "showroom-live" in url:
                delType = "m3u8"
                redis_key = "{}:{}".format("showroom", url)
                redisSR = r.redisCheck(redis_key, subkey=True)
                if redisSR:
                    urlinfo = r.redisDict(redisSR)
                    hlsurl = urlinfo["datas"]
                    datas = statusHandler.handler(0, hlsurl, delType)
                else:
                    sr = srurl.SRPlayList()
                    urlinfo = sr.getUrl(url)
                    if urlinfo["status"] == 0:
                        hlsurl = urlinfo["datas"]
                        datas = statusHandler.handler(0, hlsurl, delType)
                        r.redisSave(redis_key, datas, ex=300, subkey=True)
                    else:
                        datas = urlinfo
            else:
                delType = "picture"
                p = picdown.picdown()
                urldict = p.urlCheck(url)
                if urldict["status"] == 0:
                    sitename = urldict["type"]
                    siteurl = urldict["datas"]
                    redis_key = "{}:{}".format(sitename, siteurl)
                    redisUrls = r.redisCheck(redis_key, subkey=True)
                    if redisUrls:
                        redisUrls = r.redisDict(redisUrls)
                        imgurls = redisUrls["datas"]
                        imgtype = redisUrls["type"]
                        datas = statusHandler.handler(0, imgurls, delType)
                    else:
                        result = p.photoUrlGet(urldict)
                        imgtype = result["type"]
                        if result["status"] == 0:
                            imgurls = result["datas"]
                            datas = statusHandler.handler(0, imgurls, delType)
                            r.redisSave(redis_key, datas,
                                        ex=259200, subkey=True)
                        else:
                            datas = statusHandler.handler(
                                1, None, imgtype, message="Images Not Found")
                else:
                    datas = urldict
        else:
            datas = limitinfo
    else:
        datas = statusHandler.handler(1, None, message="Params Error")
    return jsonify(datas)


@app.route(API_DRAMA, methods=['GET'])
def drama_request():
    id_type = request.args.get("id")
    r = redisMode.redisMode()
    if id_type:
        clientip = request.remote_addr
        limitinfo = limitrate.limitIP(clientip)
        if limitinfo is None:
            if id_type == "tvbt":
                sitename = "tvbt"
                redis_key = "drama:{}".format(sitename)
                redisResult = r.redisCheck(redis_key)
                if redisResult:
                    redisResult = r.redisList(redisResult)
                    dramaContent = redisResult
                    datas = statusHandler.handler(0, dramaContent, sitename)
                else:
                    t = dramalist.tvbtsub()
                    tvbt_update_info = t.tvbtIndexInfo()
                    dramaContent = t.tvbtGetUrl(tvbt_update_info)
                    if dramaContent:
                        datas = statusHandler.handler(
                            0, dramaContent, sitename)
                        r.redisSave(redis_key, dramaContent)
                    else:
                        datas = statusHandler.handler(1, None, "No datas")
            elif id_type == "subpig":
                sitename = "subpig"
                redis_key = "drama:{}".format(sitename)
                redisResult = r.redisCheck(redis_key)
                if redisResult:
                    redisResult = r.redisList(redisResult)
                    dramaContent = redisResult
                    datas = statusHandler.handler(0, dramaContent, sitename)
                else:
                    p = dramalist.subpig()
                    subpig_update_info = p.subpigIndexInfo()
                    pool = Pool(10)
                    dramaContent = pool.map(p.subpigGetUrl, subpig_update_info)
                    pool.close()
                    pool.join
                    if dramaContent:
                        datas = statusHandler.handler(
                            0, dramaContent, sitename)
                        r.redisSave(redis_key, dramaContent)
                    else:
                        datas = statusHandler.handler(1, None, "No datas")
            elif id_type == "fixsub":
                sitename = "fixsub"
                redis_key = "drama:{}".format(sitename)
                redisResult = r.redisCheck(redis_key)
                if redisResult:
                    redisResult = r.redisList(redisResult)
                    dramaContent = redisResult
                    datas = statusHandler.handler(0, dramaContent, sitename)
                else:
                    f = dramalist.fixsub()
                    pages = 1
                    for page in range(1, pages + 1):
                        fix_page_info = f.fixPageInfo(page)
                        fix_single_page = f.fixSinglePageInfo(fix_page_info)
                        dramaContent = f.fixInfoGet(fix_single_page)
                    if dramaContent:
                        datas = statusHandler.handler(
                            0, dramaContent, sitename)
                        r.redisSave(redis_key, dramaContent)
                    else:
                        datas = statusHandler.handler(1, None, "No datas")
        else:
            datas = limitinfo
    else:
        datas = statusHandler.handler(1, None, "Params Error")
    return jsonify(datas)


@app.route(API_PROGRAM, methods=['GET'])
def program_request():
    kw = request.args.get("kw")
    if kw:
        clientip = request.remote_addr
        limitinfo = limitrate.limitIP(clientip)
        if limitinfo is None:
            keyword = kw.encode("utf-8")
            reids_key = "program:{}".format(keyword)
            r = redisMode.redisMode()
            redisKeyword = r.redisCheck(reids_key, subkey=True)
            if redisKeyword:
                rediskeyword = redisKeyword
                rediskeyword = r.redisDict(rediskeyword)
                try:
                    keyword = str(keyword, encoding="utf-8")
                except TypeError:
                    keyword = keyword
                tvinfo = rediskeyword
                tvdatas = tvinfo["datas"]
                tvurl = tvinfo["message"]
                datas = statusHandler.handler(0, tvdatas, message=tvurl)
            else:
                y = jprogram.yahooTV()
                tvinfo = y.tvInfos(keyword)
                if tvinfo["status"] == 0:
                    tvdatas = tvinfo["datas"]
                    tvurl = tvinfo["message"]
                    datas = statusHandler.handler(0, tvdatas, message=tvurl)
                    r.redisSave(reids_key, datas, ex=14400, subkey=True)
                else:
                    datas = tvinfo
        else:
            datas = limitinfo
    else:
        datas = statusHandler.handler(1, None, message="Params Error")
    return jsonify(datas)


@app.route(API_UTIME, methods=['GET'], strict_slashes=False)
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
        datas = statusHandler.handler(0, countdown_sec, message=utime)
    else:
        datas = statusHandler.handler(1, None, message="No datas")
    return jsonify(datas)


@app.route(API_ST, methods=['GET'], strict_slashes=False)
def stmovie_get():
    r = redisMode.redisMode()
    d = r.redisCheck("stinfo")
    d = r.redisList(d)
    return jsonify(d)


@app.route(API_STDL, methods=['POST'], strict_slashes=False)
def stmovie_dl():
    h = dlcore.HLSVideo()
    murl = request.get_json()
    playlist = murl["url"]
    site = h.hlsSite(playlist)
    keyvideo = h.hlsInfo(site)
    uri = h.hlsDL(keyvideo)
    dlurl = {"url": uri}
    return jsonify(dlurl)


@app.errorhandler(500)
def server_error(error):
    datas = statusHandler.handler(1, None, code=500, message="Server Error")
    return jsonify(datas)


@app.errorhandler(405)
def method_error(error):
    datas = statusHandler.handler(1, None, code=405, message="Method Error")
    return jsonify(datas)
