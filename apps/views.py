# -*- coding: utf-8 -*-
# @author AoBeom
# @create date 2017-12-22 09:45:25
# @modify date 2018-05-06 20:11:29
# @desc [Flask view main]
import os
import time
from multiprocessing.dummy import Pool

from flask import jsonify, redirect, render_template, request
from flask_login import login_required
from werkzeug import secure_filename

from apps import app, dlcore, dramalist, hlstream, jprogram, limitrate, picdown, redisMode, srurl, statusHandler, twittervideo, rikamsg, stchannel

API_VERSION = "/v1"
API_PICDOWN = API_VERSION + "/api/picdown"
API_DRAMA = API_VERSION + "/api/dramaget"
API_PROGRAM = API_VERSION + "/api/programget"
API_UTIME = API_VERSION + "/api/utime"
API_ST = API_VERSION + "/api/stinfo"
API_FRE = API_VERSION + "/api/stupdate"
API_STDL = API_VERSION + "/api/stdl"
API_UP = API_VERSION + "/api/upload"
API_VIDEOS = API_VERSION + "/api/vlist"
API_MSG = API_VERSION + "/api/msg"
API_TIK = API_VERSION + "/api/tiktok"


@app.route('/')
def index():
    return redirect("/picture")


@app.route('/picture')
def picture():
    return render_template("base_picdown.html")


@app.route('/drama')
def dramaindex():
    return render_template("base_drama.html")


@app.route('/program')
def programindex():
    return render_template("base_program.html")


@app.route('/stchannel')
def stindex():
    return render_template("base_st.html")


@app.route('/upload')
@login_required
def upload():
    return render_template("auth_upload.html")


@app.route('/hls')
@login_required
def hls():
    return render_template("auth_videolist.html")


@app.route('/rika')
@login_required
def rika():
    return render_template("auth_rika.html")


@app.route('/tiktok')
def tiktok():
    return render_template("base_tiktok.html")


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
                    hlsurl = urlinfo["data"]
                    data = statusHandler.handler(0, hlsurl, delType)
                else:
                    sr = srurl.HLSPlayList()
                    urlinfo = sr.urlRouter(url)
                    if urlinfo["status"] == 0:
                        hlsurl = urlinfo["data"]
                        data = statusHandler.handler(0, hlsurl, delType)
                        r.redisSave(redis_key, data, ex=300, subkey=True)
                    else:
                        data = urlinfo
            elif "twitter.com" in sitetype:
                delType = "twitter"
                redis_key = "{}:{}".format("twv", url)
                redistw = r.redisCheck(redis_key, subkey=True)
                if redistw:
                    urlinfo = r.redisDict(redistw)
                    twvurl = urlinfo["data"]
                    data = statusHandler.handler(0, twvurl, delType)
                else:
                    t = twittervideo.tweetimg()
                    token = t.getToken()
                    tweets = t.getTweets(token, url)
                    vurl = t.getVurl(tweets)
                    if vurl["status"] == 0:
                        twvurl = vurl["data"]
                        data = statusHandler.handler(0, twvurl, delType)
                        r.redisSave(redis_key, data, ex=300, subkey=True)
                    else:
                        data = vurl
            else:
                delType = "picture"
                p = picdown.picdown()
                urldict = p.urlCheck(url)
                if urldict["status"] == 0:
                    sitename = urldict["type"]
                    siteurl = urldict["data"]
                    redis_key = "{}:{}".format(sitename, siteurl)
                    redisUrls = r.redisCheck(redis_key, subkey=True)
                    if redisUrls:
                        redisUrls = r.redisDict(redisUrls)
                        imgurls = redisUrls["data"]
                        imgtype = redisUrls["type"]
                        data = statusHandler.handler(0, imgurls, delType)
                    else:
                        result = p.picRouter(urldict)
                        imgtype = result["type"]
                        if result["status"] == 0:
                            imgurls = result["data"]
                            data = statusHandler.handler(0, imgurls, delType)
                            r.redisSave(redis_key, data,
                                        ex=259200, subkey=True)
                        else:
                            data = statusHandler.handler(
                                1, None, imgtype, message="Images Not Found")
                else:
                    data = urldict
        else:
            data = limitinfo
    else:
        data = statusHandler.handler(1, None, message="Params Error")
    return jsonify(data)


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
                    data = statusHandler.handler(0, dramaContent, sitename)
                else:
                    t = dramalist.tvbtsub()
                    tvbt_update_info = t.tvbtIndexInfo()
                    dramaContent = t.tvbtGetUrl(tvbt_update_info)
                    if dramaContent:
                        data = statusHandler.handler(
                            0, dramaContent, sitename)
                        r.redisSave(redis_key, dramaContent)
                    else:
                        data = statusHandler.handler(1, None, "No data")
            elif id_type == "subpig":
                sitename = "subpig"
                redis_key = "drama:{}".format(sitename)
                redisResult = r.redisCheck(redis_key)
                if redisResult:
                    redisResult = r.redisList(redisResult)
                    dramaContent = redisResult
                    data = statusHandler.handler(0, dramaContent, sitename)
                else:
                    p = dramalist.subpig_rbl()
                    subpig_update_info = p.subpigIndexInfo()
                    pool = Pool(10)
                    dramaContent = pool.map(p.subpigGetUrl, subpig_update_info)
                    pool.close()
                    pool.join
                    if dramaContent:
                        data = statusHandler.handler(
                            0, dramaContent, sitename)
                        r.redisSave(redis_key, dramaContent)
                    else:
                        data = statusHandler.handler(1, None, "No data")
            elif id_type == "fixsub":
                sitename = "fixsub"
                redis_key = "drama:{}".format(sitename)
                redisResult = r.redisCheck(redis_key)
                if redisResult:
                    redisResult = r.redisList(redisResult)
                    dramaContent = redisResult
                    data = statusHandler.handler(0, dramaContent, sitename)
                else:
                    f = dramalist.fixsub()
                    pages = 1
                    for page in range(1, pages + 1):
                        fix_page_info = f.fixPageInfo(page)
                        fix_single_page = f.fixSinglePageInfo(fix_page_info)
                        dramaContent = f.fixInfoGet(fix_single_page)
                    if dramaContent:
                        data = statusHandler.handler(
                            0, dramaContent, sitename)
                        r.redisSave(redis_key, dramaContent)
                    else:
                        data = statusHandler.handler(1, None, "No data")
        else:
            data = limitinfo
    else:
        data = statusHandler.handler(1, None, "Params Error")
    return jsonify(data)


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
                tvdata = tvinfo["data"]
                tvurl = tvinfo["message"]
                data = statusHandler.handler(0, tvdata, message=tvurl)
            else:
                y = jprogram.yahooTV()
                tvinfo = y.tvInfos(keyword, code)
                if tvinfo["status"] == 0:
                    tvdata = tvinfo["data"]
                    tvurl = tvinfo["message"]
                    data = statusHandler.handler(0, tvdata, message=tvurl)
                    r.redisSave(redis_key, data, ex=14400, subkey=True)
                else:
                    data = tvinfo
        else:
            data = limitinfo
    else:
        data = statusHandler.handler(1, None, message="Params Error")
    return jsonify(data)


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
        data = statusHandler.handler(0, countdown_sec, message=utime)
    else:
        data = statusHandler.handler(1, None, message="No data")
    return jsonify(data)


@app.route(API_ST, methods=['GET'], strict_slashes=False)
def stmovie_get():
    r = redisMode.redisMode()
    data = {}
    stinfo = r.redisCheck("stinfo")
    if stinfo:
        stinfo = r.redisList(stinfo)
    else:
        data = statusHandler.handler(1, None, message="No data")
        return jsonify(data)
    stutime = r.redisCheck("st:utime")
    clientip = request.remote_addr
    limitinfo = limitrate.limitIP(clientip)
    if stinfo:
        if limitinfo is None:
            data = statusHandler.handler(0, stinfo, message=stutime)
        else:
            data = limitinfo
    else:
        data = statusHandler.handler(1, None, message="No data")
    return jsonify(data)


@app.route(API_FRE, methods=['GET'], strict_slashes=False)
def stmovie_fresh():
    r = redisMode.redisMode()
    data = {}
    st_key = "st:update"
    st_state = r.redisCheck(st_key)
    if st_state:
        ttl = r.redisTTL(st_key)
        data = statusHandler.handler(0, "true", message="ttl: " + str(ttl))
    else:
        data = statusHandler.handler(1, "false")
        value = request.args.get("k")
        if value:
            r.redisSave(st_key, "true", ex=7200)
            st = stchannel.stMovies()
            st_info = st.stMovieInfos()
            infos = st.stGetUrl(st_info)
            r.redisSave("stinfo", infos)
    return jsonify(data)


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
            data = statusHandler.handler(0, uri)
        else:
            data = limitinfo
    else:
        data = statusHandler.handler(1, None, message="No data")
    return jsonify(data)


@app.errorhandler(500)
def server_5xx(error):
    return render_template("error_5xx.html")


@app.errorhandler(405)
def method_405(error):
    data = statusHandler.handler(1, None, code=405, message="Method Error")
    return jsonify(data)


@app.errorhandler(404)
def server_404(error):
    return render_template("error_not_found.html")


@app.route(API_UP, methods=['GET', 'POST'], strict_slashes=False)
@login_required
def upload_file():
    if request.method == 'POST':
        r = redisMode.redisMode()
        h = hlstream.hlsegment()
        file = request.files['file']
        filename = secure_filename(file.filename)
        mainpath = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
        video = os.path.join(mainpath, "videos", filename)
        file.save(video)
        playlist = h.segment(video, "media")
        redis_key = "playlist:{}".format(playlist)
        data = statusHandler.handler(0, playlist)
        r.redisSave(redis_key, data, ex=604800, subkey=True)
        return jsonify(data)
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
    return render_template("single_player.html", url=url)


@app.route(API_MSG, methods=['GET'], strict_slashes=False)
@login_required
def rika_msg():
    mtype = request.args.get("type")
    page = request.args.get("page")
    mtype = int(mtype)
    msg = rikamsg.rikaMsg()
    pages = msg.keya_pages_query(mtype)
    if mtype == 100:
        if page:
            allinfo = msg.keya_allinfo_query(page)
            return jsonify(allinfo)
    else:
        if page:
            allinfo = msg.keya_media_query(page, mtype)
            return jsonify(allinfo)
    return jsonify(pages)


@app.route(API_TIK, methods=['GET'], strict_slashes=False)
def tiktok_get():
    r = redisMode.redisMode()
    data = {}
    tikinfo = r.redisCheck("tiktok")
    if tikinfo:
        tikinfo = r.redisList(tikinfo)
    else:
        data = statusHandler.handler(1, None, message="No data")
    clientip = request.remote_addr
    limitinfo = limitrate.limitIP(clientip)
    if tikinfo:
        if limitinfo is None:
            data = statusHandler.handler(0, tikinfo)
        else:
            data = limitinfo
    else:
        data = statusHandler.handler(1, None, message="No data")
    return jsonify(data)
