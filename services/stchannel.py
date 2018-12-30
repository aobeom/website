# coding:utf-8
# @author AoBeom
# @create date 2018-09-09 22:13:40
# @modify date 2018-12-30 16:15:54
# @desc [description]
import datetime
import json
import os
import sys
import time

import requests

from lib import dlcore

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)

from modules import mongoSet

db = mongoSet.dbSTchannel()


class stMovies(object):
    def __init__(self):
        self.user_api = "https://st-api.st-channel.jp/v1/users"
        self.movie_api = "https://st-api.st-channel.jp/v1/movies?"
        self.headers = {
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 7.1.1; E6533 Build/32.4.A.0.160)",
            "Content-Type": "application/json; charset=UTF-8"
        }

    def __dformat(self, date):
        dateformat = datetime.datetime.strptime(
            date, '%Y-%m-%dT%H:%M:%S+09:00')
        dateformat = str(dateformat)
        darray = time.strptime(dateformat, "%Y-%m-%d %H:%M:%S")
        dformats = time.strftime("%Y-%m-%d %H:%M:%S", darray)
        return dformats

    def stToken(self):
        token = db.get_token()
        if token:
            authToken = token["token"]
        else:
            userInfo = requests.post(
                self.user_api, headers=self.headers, timeout=30).text
            authToken = json.loads(userInfo)["api_token"]
            db.refresh_token(authToken)
        return authToken

    def stMovieInfos(self):
        userHeader = self.headers
        authToken = self.stToken()
        userHeader["Authorization"] = "Bearer " + authToken
        api_param = {
            "since_id": 0,
            "device_type": 2,
            "since_order": 0,
            "sort": "order"
        }
        response = requests.get(
            self.movie_api, headers=userHeader, params=api_param, timeout=30)
        code = response.status_code
        while code != 200:
            authToken = self.stToken()
            userHeader["Authorization"] = "Bearer " + authToken
            response = requests.get(
                self.movie_api, headers=userHeader, params=api_param, timeout=30)
            code = response.status_code
        stInfo = response.text
        return stInfo

    def stGetUrl(self, info):
        movies = json.loads(info)["movies"]
        st_infos = []
        for i in movies:
            st_new = {}
            st_title = i["title"].strip()
            st_movie = requests.utils.unquote(i["movie_url_everyone"]).replace(
                "ulizasekailab", "https").replace("videoquery=", "")
            st_thumbnail = i["thumbnail_path"]
            st_date = self.__dformat(i["publish_start_date"])
            st_new["title"] = st_title
            st_new["murl"] = st_movie
            st_new["purl"] = st_thumbnail
            st_new["date"] = st_date
            st_infos.append(st_new)
        return st_infos


def main():
    times = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    mongoSet.updateTime("stchannel", times)

    st = stMovies()
    st_info = st.stMovieInfos()
    st_data = st.stGetUrl(st_info)

    update_data = db.updateMovieList(st_data)
    db.updateData(st_data)

    hls = dlcore.HLSVideo()

    update_num = len(update_data)

    if update_num != 0:
        print("Update [{}]".format(update_num))
        for u in update_data:
            playlist = u["murl"]
            purl = u["purl"]
            keyvideo = hls.hlsInfo(playlist)
            media_path = hls.hlsDL(keyvideo)
            db.updateMoviePath(purl, media_path)
            time.sleep(3)
    else:
        print("No Update")
    print("Update time: " + times)


if __name__ == "__main__":
    main()