# -*- coding: utf-8 -*-
# @author AoBeom
# @create date 2017-12-22 09:45:25
# @modify date 2018-07-07 22:16:55
# @desc [Flask view main]
import os
import time

from flask import jsonify, redirect, render_template, request
from flask_login import login_required
from flask_restful import reqparse, Resource
from werkzeug import secure_filename
from werkzeug.datastructures import FileStorage

from apps import app, api, hlstream, jprogram, picdown, redisMode, srurl, rikamsg

APIVERSION = "/api/v1"
redis = redisMode.redisMode()


def limitIP(ip):
    keyname = "ip:{}".format(ip)
    limit_ip = redis.redisCheck(keyname)
    if limit_ip is not None and int(limit_ip) > 9:
        return False
    else:
        redis.redisCounter(keyname)
        return True


def handler(status, data, **other):
    d = {}
    d["status"] = status
    d["message"] = data
    d["data"] = other
    return d


@app.errorhandler(500)
def server_5xx(error):
    return render_template("error_5xx.html")


@app.errorhandler(405)
def method_405(error):
    data = handler(1, None, code=405, message="Method Error")
    return jsonify(data)


@app.errorhandler(404)
def server_404(error):
    return render_template("error_not_found.html")


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
def tiktok_index():
    return render_template("base_tiktok.html")


class Media(Resource):
    def get(self, target):
        parser = reqparse.RequestParser()
        parser.add_argument('url', required=True, help="URL is required")
        para = parser.parse_args()
        url = para.get("url")
        targets = ["news", "hls"]
        if target not in targets:
            return handler(1, "The type is not supported")
        else:
            clientip = request.remote_addr
            limitinfo = limitIP(clientip)
            if limitinfo:
                if target == "news":
                    p = picdown.picdown()
                    urldict = p.urlCheck(url)
                    if urldict:
                        sitename = urldict["type"]
                        siteurl = urldict["data"]
                        redis_key = "{}:{}".format(sitename, siteurl)
                        redisUrls = redis.redisCheck(redis_key, subkey=True)
                        if redisUrls:
                            imgurls = redis.redisList(redisUrls)
                            return handler(0, "The news has a total of {} pictures".format(len(imgurls)), type=target, entities=imgurls)
                        else:
                            imgurls = p.picRouter(urldict)
                            if imgurls:
                                redis.redisSave(
                                    redis_key, imgurls, ex=259200, subkey=True)
                                return handler(0, "The news has a total of {} pictures".format(len(imgurls)), type=target, entities=imgurls)
                            else:
                                return handler(1, "This news has no pictures")
                    else:
                        return handler(1, "The news site is not supported")
                elif target == "hls":
                    sr = srurl.HLSPlayList()
                    urltype = sr.urlCheck(url)
                    if urltype:
                        site = urltype[0]
                        hls_url = urltype[1]
                        redis_key = "{}:{}".format("hlsm3u8", hls_url)
                        redisSR = redis.redisCheck(redis_key, subkey=True)
                        if redisSR:
                            print("Good")
                            m3u8_url = redisSR
                            return handler(0, "This is a {} playlist".format(site), type=target, entities=m3u8_url)
                        else:
                            m3u8_url = sr.urlRouter(urltype)
                            if m3u8_url:
                                redis.redisSave(
                                    redis_key, m3u8_url, ex=300, subkey=True)
                                return handler(0, "This is a {} playlist".format(site), type=target, entities=m3u8_url)
                            else:
                                return handler(1, "No content")
                    else:
                        return handler(1, "The hls site is not supported")
            else:
                return handler(1, "Too many requests per second")


class Drama(Resource):
    def get(self, subname):
        subnames = ["tvbt", "subpig", "fixsub"]
        if subname not in subnames:
            return handler(1, "The subtitle group does not exist")
        else:
            clientip = request.remote_addr
            limitinfo = limitIP(clientip)
            if limitinfo:
                redis_key = "drama:{}".format(subname)
                redisResult = redis.redisCheck(redis_key)
                if redisResult:
                    redisResult = redis.redisList(redisResult)
                    dramaContent = redisResult
                    return handler(0, "{} drama listing".format(subname), name=subname, entities=dramaContent)
                else:
                    return handler(1, "No drama data")
            else:
                return handler(1, "Too many requests per second")


class DramaTime(Resource):
    def get(self):
        utime = redis.conn.get("drama:utime")
        try:
            utime = str(utime, encoding="utf-8")
        except TypeError:
            utime = utime
        if utime:
            utime_timestamp = int(time.mktime(
                time.strptime(str(utime), '%Y-%m-%d %H:%M:%S')))
            ntime_timestamp = int(time.time())
            ltime_timestamp = utime_timestamp + 14400
            sec = ltime_timestamp - ntime_timestamp
            return handler(0, "Drama update time", second=sec, time=utime)
        else:
            return handler(1, "No data")


class Program(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('kw', required=True, help="Keyword is required")
        parser.add_argument('ac', required=True,
                            help="Region code is required")
        para = parser.parse_args()
        kw = para["kw"]
        ac = para["ac"]
        if kw and ac:
            clientip = request.remote_addr
            limitinfo = limitIP(clientip)
            if limitinfo:
                keyword = kw.encode("utf-8")
                redis_key = "{}:{}".format(ac, keyword)
                redisKeyword = redis.redisCheck(redis_key, subkey=True)
                if redisKeyword:
                    rediskeyword = redis.redisList(redisKeyword)
                    try:
                        keyword = str(keyword, encoding="utf-8")
                    except TypeError:
                        keyword = keyword
                    tvinfo = rediskeyword
                    tvdata = tvinfo[0]
                    tvurl = tvinfo[1]
                    return handler(0, "Program information", ori_url=tvurl, entities=tvdata)
                else:
                    y = jprogram.yahooTV()
                    tvinfo = y.tvInfos(keyword, ac)
                    if tvinfo:
                        redis.redisSave(redis_key, tvinfo,
                                        ex=14400, subkey=True)
                        tvdata = tvinfo[0]
                        tvurl = tvinfo[1]
                        return handler(0, "Program information", ori_url=tvurl, entities=tvdata)
                    else:
                        return handler(1, "No information")
            else:
                return handler(1, "Too many requests per second")
        else:
            return handler(1, "Parameter error")


class Stchannel(Resource):
    def get(self):
        stinfo = redis.redisCheck("stinfo")
        stutime = redis.redisCheck("st:utime")
        clientip = request.remote_addr
        limitinfo = limitIP(clientip)
        if limitinfo:
            if stinfo:
                stinfo = redis.redisList(stinfo)
                return handler(0, "STchannel video listing", time=stutime, entities=stinfo)
            else:
                return handler(1, "No listing")
        else:
            return handler(1, "Too many requests per second")


class UploadFile(Resource):
    @login_required
    def get(self):
        playlists = redis.redisKeys("playlist:*")
        total = len(playlists)
        return handler(0, "Total video", number=total)

    @login_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('file', type=FileStorage, location='files')
        args = parser.parse_args()
        file = args['file']
        filename = secure_filename(file.filename)
        mainpath = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
        video = os.path.join(mainpath, "videos", filename)
        file.save(video)
        h = hlstream.hlsegment()
        playlist = h.segment(video, "media")
        redis_key = "playlist:{}".format(playlist)
        data = handler(0, "Video url", path=playlist)
        redis.redisSave(redis_key, data, ex=604800, subkey=True)
        return data


@app.route('/hls/<code>')
@login_required
def subhls(code):
    playlists = redis.redisKeys("playlist:*")
    total = len(playlists)
    if int(code) <= total and int(code) != 0:
        index = int(code) - 1
        playlist = playlists[index]
        if playlist:
            data = redis.redisCheck(playlist)
            data = redis.redisDict(data)
            url = data["data"]["path"]
            print(url)
            return render_template("single_player.html", url=url)
    else:
        return handler(1, "No video")


class RikaMsg(Resource):
    @login_required
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('type', required=True, help="Type is required")
        parser.add_argument('page', help="Page code is required")
        para = parser.parse_args()
        mtype = int(para["type"])
        page = para["page"]
        msg = rikamsg.rikaMsg()
        if mtype in range(4) or mtype == 100:
            if page:
                if mtype == 100:
                    allinfo = msg.keya_allinfo_query(page)
                    if allinfo:
                        return handler(0, "All message", entities=allinfo)
                    else:
                        return handler(1, "No data")
                else:
                    partinfo = msg.keya_media_query(page, mtype)
                    if partinfo:
                        return handler(0, "Part message", entities=partinfo)
                    else:
                        return handler(1, "No data")
            else:
                pages = msg.keya_pages_query(mtype)
                return handler(0, "Total pages", pages=pages)
        else:
            return handler(1, "No such type, only 0-4 or 100")


class Tiktok(Resource):
    def get(self):
        tikinfo = redis.redisCheck("tik:info")
        tikutime = redis.redisCheck("tik:utime")
        clientip = request.remote_addr
        limitinfo = limitIP(clientip)
        if limitinfo:
            if tikinfo:
                tikinfo = redis.redisList(tikinfo)
                return handler(0, "Tiktok video listing", time=tikutime, entities=tikinfo)
            else:
                return handler(1, "No listing")
        else:
            return handler(1, "Too many requests per second")


api.add_resource(Media, APIVERSION + '/media/<target>')
api.add_resource(Drama, APIVERSION + '/drama/<subname>')
api.add_resource(DramaTime, APIVERSION + '/drama/time')
api.add_resource(Program, APIVERSION + '/program')
api.add_resource(Stchannel, APIVERSION + '/stchannel')
api.add_resource(UploadFile, APIVERSION + '/upload')
api.add_resource(RikaMsg, APIVERSION + '/rikamsg')
api.add_resource(Tiktok, APIVERSION + '/tiktok')
