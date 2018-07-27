# coding=utf-8
# @author AoBeom
# @create date 2018-07-27 20:55:14
# @modify date 2018-07-27 20:55:14
# @desc [stchannel video download]
import requests
import json
import datetime
import time
import urllib
import redisMode


class stMovies(object):
    def __init__(self):
        self.user_api = "https://st-api.st-channel.jp/v1/users"
        self.movie_api = "https://st-api.st-channel.jp/v1/movies?"
        self.headers = {
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 7.1.1; E6533 Build/32.4.A.0.160)",
            "Content-Type": "application/json; charset=UTF-8"
        }
        self.redis = redisMode.redisMode(crond=True)

    def __dformat(self, date):
        dateformat = datetime.datetime.strptime(
            date, '%Y-%m-%dT%H:%M:%S+09:00')
        dateformat = str(dateformat)
        darray = time.strptime(dateformat, "%Y-%m-%d %H:%M:%S")
        dformats = time.strftime("%Y-%m-%d %H:%M:%S", darray)
        return dformats

    def stToken(self, delkey=False):
        r = self.redis
        token_redis = "st:token"
        if delkey:
            token = r.redisDel(token_redis)
        else:
            token = r.redisCheck(token_redis)
        if token:
            authToken = token
        else:
            userInfo = requests.post(
                self.user_api, headers=self.headers, timeout=30).text
            authToken = json.loads(userInfo)["api_token"]
            r.redisSave(token_redis, authToken)
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
            authToken = self.stToken(delkey=True)
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
            st_movie = urllib.unquote(i["movie_url_everyone"]).replace(
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
    st = stMovies()
    st_info = st.stMovieInfos()
    infos = st.stGetUrl(st_info)
    r = redisMode.redisMode(crond=True)
    r.redisSave("stinfo", infos)
    r.redisSave("st:utime", times)


if __name__ == "__main__":
    main()
