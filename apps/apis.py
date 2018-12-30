# -*- coding: utf-8 -*-
# @author AoBeom
# @create date 2017-12-22 09:45:25
# @modify date 2018-12-30 18:37:42
# @desc [Flask view main]
import time

from flask import request, g
from flask_restful import reqparse, Resource

from modules import jprogram, picdown, srurl, tweetV, redisMode
from modules.mongoSet import dbAuth, dbMedia, dbDrama, dbCrond, dbProgram, dbSTchannel, dbRikaMsg
from modules.config import handler
from apps import authen, api

# UploadFile API
# import os
# from werkzeug import secure_filename
# from werkzeug.datastructures import FileStorage
# from modules import hlstream

APIVERSION = "/api/v1"
redis = redisMode.redisMode()
Crond = dbCrond()
Users = dbAuth()
Medias = dbMedia()
Dramas = dbDrama()
STchan = dbSTchannel()
Programs = dbProgram()
Rika = dbRikaMsg()
Medias.setLiveTTL(600)
Programs.setTTL(14400)


def limitIP(ip):
    keyname = "ip:{}".format(ip)
    limit_ip = redis.redisCheck(keyname)
    if limit_ip is not None and int(limit_ip) > 9:
        return False
    else:
        redis.redisCounter(keyname)
        return True


@authen.verify_token
def verify_token(token):
    g.user = None
    token_check = Users.checkToken(token)
    if token_check:
        g.user = token_check
        return True
    return False


class Media(Resource):
    def get(self, target):
        parser = reqparse.RequestParser()
        parser.add_argument('url', required=True, help="URL is required")
        para = parser.parse_args()
        url = para.get("url")
        targets = ["news", "hls", "twitter"]
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
                        data = Medias.getData(siteurl)
                        if data:
                            imgurls = data["source"]
                            return handler(0, "The news has a total of {} pictures".format(len(imgurls)), type=target, entities=imgurls)
                        else:
                            imgurls = p.picRouter(urldict)
                            if imgurls:
                                Medias.update(target, sitename, siteurl, imgurls)
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
                        data = Medias.getLiveData(hls_url)
                        if data:
                            m3u8_url = data["source"]
                            return handler(0, "This is a {} playlist".format(site), type=target, entities=m3u8_url)
                        else:
                            m3u8_url = sr.urlRouter(urltype)
                            if m3u8_url:
                                Medias.updateLive(target, site, hls_url, m3u8_url)
                                return handler(0, "This is a {} playlist".format(site), type=target, entities=m3u8_url)
                            else:
                                return handler(1, "No content")
                    else:
                        return handler(1, "The hls site is not supported")
                elif target == "twitter":
                    url = url.split("?")[0]
                    data = Medias.getData(url)
                    if data:
                        tweet_vurl = data["source"]
                        return handler(0, "This is a Twitter Video url", type=target, entities=tweet_vurl)
                    else:
                        site = "twitter.com"
                        tweet_vurl = tweetV.getVideoURL(url)
                        if tweet_vurl:
                            Medias.update(target, site, url, tweet_vurl)
                            return handler(0, "This is a Twitter Video url", type=target, entities=tweet_vurl)
                        else:
                            return handler(1, "This url has no video")
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
                data = Dramas.getData(subname)
                if data:
                    dramaContent = data
                    return handler(0, "{} drama listing".format(subname), name=subname, entities=dramaContent)
                else:
                    return handler(1, "No drama data")
            else:
                return handler(1, "Too many requests per second")


class DramaTime(Resource):
    def get(self):
        utime = Crond.getData("drama")["time"]
        if utime:
            utime_timestamp = int(time.mktime(
                time.strptime(utime, '%Y-%m-%d %H:%M:%S')))
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
        parser.add_argument('ac', required=True, help="Region code is required")
        para = parser.parse_args()
        kw = para["kw"]
        ac = para["ac"]
        if kw and ac:
            clientip = request.remote_addr
            limitinfo = limitIP(clientip)
            if limitinfo:
                keyword = kw.encode("utf-8")
                data = Programs.getData(kw, ac)
                if data:
                    tvdata = data["prog_info"]
                    tvurl = data["yahoo_url"]
                    return handler(0, "Program information", ori_url=tvurl, entities=tvdata)
                else:
                    y = jprogram.yahooTV()
                    tvinfo = y.tvInfos(keyword, ac)
                    if tvinfo:
                        tvdata = tvinfo[0]
                        tvurl = tvinfo[1]
                        Programs.update(kw, ac, tvurl, tvdata)
                        return handler(0, "Program information", ori_url=tvurl, entities=tvdata)
                    else:
                        return handler(1, "No information")
            else:
                return handler(1, "Too many requests per second")
        else:
            return handler(1, "Parameter error")


class Stchannel(Resource):
    def get(self):
        clientip = request.remote_addr
        limitinfo = limitIP(clientip)
        if limitinfo:
            data = STchan.top15()
            if data:
                stutime = Crond.getData("stchannel")["time"]
                stinfo = list(data)
                return handler(0, "STchannel video listing", time=stutime, entities=stinfo)
            else:
                return handler(1, "No listing")
        else:
            return handler(1, "Too many requests per second")


class RikaMsg(Resource):
    decorators = [authen.login_required]

    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('type', required=True, help="Type is required")
        parser.add_argument('page', help="Page code is required")
        para = parser.parse_args()
        mtype = int(para["type"])
        page = para["page"]
        if mtype in range(4) or mtype == 100:
            type_info = Rika.getType(mtype)
            pages = Rika.getPages(mtype)
            if page:
                if mtype == 100:
                    allinfo = Rika.getPageInfo(page)
                    if allinfo:
                        return handler(0, "All message", entities=allinfo, pages=pages)
                    else:
                        return handler(1, "No data")
                else:
                    partinfo = Rika.getPageInfo(page, mtype)
                    if partinfo:
                        return handler(0, "{} message".format(type_info), entities=partinfo, pages=pages)
                    else:
                        return handler(1, "No data")
            else:
                return handler(1, "Type and Page is required")
        else:
            return handler(1, "No such type, only 0-3 or 100")


# class UploadFile(Resource):
#     decorators = [authen.login_required]

#     def get(self):
#         playlists = redis.redisKeys("playlist:*")
#         total = len(playlists)
#         return handler(0, "Total video", number=total)

#     def post(self):
#         parser = reqparse.RequestParser()
#         parser.add_argument('file', type=FileStorage, location='files')
#         args = parser.parse_args()
#         file = args['file']
#         filename = secure_filename(file.filename)
#         mainpath = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
#         video = os.path.join(mainpath, "videos", filename)
#         file.save(video)
#         h = hlstream.hlsegment()
#         playlist = h.segment(video, "media")
#         redis_key = "playlist:{}".format(playlist)
#         data = handler(0, "Video url", path=playlist)
#         redis.redisSave(redis_key, data, ex=604800, subkey=True)
#         return data


api.add_resource(Media, APIVERSION + '/media/<target>')
api.add_resource(Drama, APIVERSION + '/drama/<subname>')
api.add_resource(DramaTime, APIVERSION + '/drama/time')
api.add_resource(Program, APIVERSION + '/program')
api.add_resource(Stchannel, APIVERSION + '/stchannel')
api.add_resource(RikaMsg, APIVERSION + '/rikamsg')
# api.add_resource(UploadFile, APIVERSION + '/upload')
