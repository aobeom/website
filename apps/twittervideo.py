# -*- coding:utf-8 -*-
# @author AoBeom
# @create date 2018-04-14 13:46:14
# @modify date 2018-04-14 13:46:14
# @desc [twitter video]
import json
import os

import requests

import statusHandler


class tweetimg(object):
    def __init__(self):
        self.oauth = "https://api.twitter.com/oauth2/token"
        self.statuses = "https://api.twitter.com/1.1/statuses/user_timeline.json"
        workdir = os.path.dirname(os.path.abspath(__file__))
        devfile = os.path.join(workdir, "twitterdev.json")
        f = open(devfile, "rb")
        devinfo = json.loads(f.read())
        self.consumer_key = devinfo["consumer_key"]
        self.consumer_secret = devinfo["consumer_secret"]
        f.close()

    def getToken(self, apifile=None):
        host = self.oauth
        headers = {
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"}
        auth = (self.consumer_key, self.consumer_secret)
        data = {'grant_type': 'client_credentials'}
        r = requests.post(host, headers=headers, auth=auth, data=data)
        code = r.status_code
        if code == 200:
            token = json.loads(r.text)["access_token"]
            result = statusHandler.handler(0, token, code=code, types="token")
        else:
            result = statusHandler.handler(
                1, None, code=code, types="token", message="Authentication failure")
        return result

    def getTweets(self, token_data, status_url):
        if token_data["status"] == 0:
            token = token_data["datas"]
            url_info = status_url.split("/")
            user = url_info[3]
            maxid = url_info[-1].split("?")[0]
            host = self.statuses
            headers = {"Authorization": "Bearer " + token}
            params = {"screen_name": user, "count": 1, "max_id": maxid}
            r = requests.get(host, headers=headers, params=params, timeout=30)
            if r.status_code == 200:
                user_tweets = json.loads(r.text)
                if user_tweets:
                    result = statusHandler.handler(
                        0, user_tweets, types="tweets")
                else:
                    result = statusHandler.handler(
                        1, None, types="tweets", message="No tweets")
            else:
                result = statusHandler.handler(
                    1, None, types="tweets", message="No tweets")
        else:
            result = token_data
        return result

    def getVurl(self, tweet_data):
        if tweet_data["status"] == 0:
            if tweet_data["datas"]:
                tweets = tweet_data["datas"][0]
                if "extended_entities" in tweets:
                    media = tweets["extended_entities"]["media"]
                    media = media[0]
                    if "video_info" in media:
                        video_info = media["video_info"]["variants"]
                        for v in video_info:
                            if "bitrate" in v:
                                if v["bitrate"] == 2176000:
                                    video = v["url"]
                                    result = statusHandler.handler(
                                        0, video, types="video url")
                    else:
                        result = statusHandler.handler(
                            1, None, types="video", message="No video url")
                else:
                    result = statusHandler.handler(
                        1, None, types="video", message="No media")
            else:
                result = statusHandler.handler(
                    0, None, types="video", message="No video url")
        else:
            result = tweet_data
        return result
