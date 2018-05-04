# -*- coding: utf-8 -*-
# @author AoBeom
# @create date 2017-12-22 09:45:25
# @modify date 2018-04-14 13:46:34
# @desc [Flask view main]
import os
import time
from multiprocessing.dummy import Pool

from flask import jsonify, redirect, render_template, request
from flask_login import login_required
from werkzeug import secure_filename

from apps import app, dlcore, dramalist, hlstream, jprogram, limitrate, picdown, redisMode, srurl, statusHandler, twittervideo, rikamsg

API_VERSION = "/v1"
API_PICDOWN = API_VERSION + "/api/picdown"
API_DRAMA = API_VERSION + "/api/dramaget"
API_PROGRAM = API_VERSION + "/api/programget"
API_UTIME = API_VERSION + "/api/utime"
API_ST = API_VERSION + "/api/stinfo"
API_STDL = API_VERSION + "/api/stdl"
API_UP = API_VERSION + "/api/upload"
API_VIDEOS = API_VERSION + "/api/vlist"
API_MSG = API_VERSION + "/api/msg"


@app.route('/')
def index():
    return redirect("/picture")


@app.route('/picture')
def picture():
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


@app.route('/upload')
@login_required
def upload():
    return render_template("player.html")


@app.route('/hls')
@login_required
def hls():
    return render_template("hlslist.html")


@app.route('/rika')
@login_required
def rika():
    return render_template("rika.html")


@app.route(API_PICDOWN, methods=['GET'])
def pic_request():
    url = request.args.get("url")
    r = redisMode.redisMode()
    if url:
        clientip = request.remote_addr
        limitinfo = limitrate.limitIP(clientip)
        if limitinfo is None:
            sites = ["www.showroom-live.com", "live.line.me"]
            sitetype = url.split("/")[2]
            if sitetype in sites:
                delType = "m3u8"
                redis_key = "{}:{}".format("hlsmeu8", url)
                redisSR = r.redisCheck(redis_key, subkey=True)
                if redisSR:
                    urlinfo = r.redisDict(redisSR)
                    hlsurl = urlinfo["datas"]
                    datas = statusHandler.handler(0, hlsurl, delType)
                else:
                    sr = srurl.HLSPlayList()
                    urlinfo = sr.urlRouter(url)
                    if urlinfo["status"] == 0:
                        hlsurl = urlinfo["datas"]
                        datas = statusHandler.handler(0, hlsurl, delType)
                        r.redisSave(redis_key, datas, ex=300, subkey=True)
                    else:
                        datas = urlinfo
            elif "twitter.com" in sitetype:
                delType = "twitter"
                redis_key = "{}:{}".format("twv", url)
                redistw = r.redisCheck(redis_key, subkey=True)
                if redistw:
                    urlinfo = r.redisDict(redistw)
                    twvurl = urlinfo["datas"]
                    datas = statusHandler.handler(0, twvurl, delType)
                else:
                    t = twittervideo.tweetimg()
                    token = t.getToken()
                    tweets = t.getTweets(token, url)
                    vurl = t.getVurl(tweets)
                    if vurl["status"] == 0:
                        twvurl = vurl["datas"]
                        datas = statusHandler.handler(0, twvurl, delType)
                        r.redisSave(redis_key, datas, ex=300, subkey=True)
                    else:
                        datas = vurl
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
                        result = p.picRouter(urldict)
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
    code = request.args.get("ac")
    if kw:
        clientip = request.remote_addr
        limitinfo = limitrate.limitIP(clientip)
        if limitinfo is None:
            keyword = kw.encode("utf-8")
            redis_key = "{}:{}".format(code, keyword)
            r = redisMode.redisMode()
            redisKeyword = r.redisCheck(redis_key, subkey=True)
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
                tvinfo = y.tvInfos(keyword, code)
                if tvinfo["status"] == 0:
                    tvdatas = tvinfo["datas"]
                    tvurl = tvinfo["message"]
                    datas = statusHandler.handler(0, tvdatas, message=tvurl)
                    r.redisSave(redis_key, datas, ex=14400, subkey=True)
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
    datas = {}
    stinfo = r.redisCheck("stinfo")
    if stinfo:
        stinfo = r.redisList(stinfo)
    else:
        datas = statusHandler.handler(1, None, message="No datas")
        return jsonify(datas)
    stutime = r.redisCheck("st:utime")
    clientip = request.remote_addr
    limitinfo = limitrate.limitIP(clientip)
    if stinfo:
        if limitinfo is None:
            datas = statusHandler.handler(0, stinfo, message=stutime)
        else:
            datas = limitinfo
    else:
        datas = statusHandler.handler(1, None, message="No datas")
    return jsonify(datas)


@app.route(API_STDL, methods=['POST'], strict_slashes=False)
def stmovie_dl():
    h = dlcore.HLSVideo()
    murl = request.get_json()
    playlist = murl["url"]
    keyvideo = h.hlsInfo(playlist)
    uri = h.hlsDL(keyvideo)
    clientip = request.remote_addr
    limitinfo = limitrate.limitIP(clientip)
    if uri:
        if limitinfo is None:
            datas = statusHandler.handler(0, uri)
        else:
            datas = limitinfo
    else:
        datas = statusHandler.handler(1, None, message="No datas")
    return jsonify(datas)


@app.errorhandler(500)
def server_error(error):
    datas = statusHandler.handler(1, None, code=500, message="Server Error")
    return jsonify(datas)


@app.errorhandler(405)
def method_error(error):
    datas = statusHandler.handler(1, None, code=405, message="Method Error")
    return jsonify(datas)


@app.route(API_UP, methods=['GET', 'POST'], strict_slashes=False)
@login_required
def upload_file():
    if request.method == 'POST':
        r = redisMode.redisMode()
        h = hlstream.hlsegment()
        file = request.files['file']
        filename = secure_filename(file.filename)
        video = os.path.join(os.getcwd(), "videos", filename)
        file.save(video)
        playlist = h.segment(video, "media")
        redis_key = "playlist:{}".format(playlist)
        datas = statusHandler.handler(0, playlist)
        r.redisSave(redis_key, datas, ex=604800, subkey=True)
        return jsonify(datas)
    if request.method == 'GET':
        r = redisMode.redisMode()
        playlists = r.redisKeys("playlist:*")
        totals = str(len(playlists))
        return totals


@app.route('/hls/<code>')
@login_required
def subhls(code):
    code = int(code) - 1
    r = redisMode.redisMode()
    playlists = r.redisKeys("playlist:*")
    playlist = playlists[code]
    url = r.redisCheck(playlist)
    url = r.redisDict(url)
    return render_template("vpage.html", url=url)


@app.route(API_MSG, methods=['GET'], strict_slashes=False)
@login_required
def rika_msg():
    msg = rikamsg.rikaMsg()
    pages = msg.keya_pages_query()
    page = request.args.get("page")
    if page:
        allinfo = msg.keya_allinfo_query(page)
        return jsonify(allinfo)
    return jsonify(pages)
