# coding=utf-8
import json

import requests

twitter_key = ""
twitter_secret = ""
token = ""


def getToken():
    # https://developer.twitter.com/en/docs/basics/authentication/api-reference/token
    oauth_host = "https://api.twitter.com/oauth2/token"
    # get api info
    consumer_key = twitter_key
    consumer_secret = twitter_secret
    # auth token
    # https://dev.twitter.com/oauth/application-only
    headers = {
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"
    }
    auth_info = (consumer_key, consumer_secret)
    auth_data = {'grant_type': 'client_credentials'}
    res = requests.post(oauth_host, headers=headers, auth=auth_info, data=auth_data)
    # https://developer.twitter.com/en/docs/basics/authentication/FAQ
    if res.status_code == 200:
        res_json = json.loads(res.text)
        token = res_json["access_token"]
        return token


def getVideoURL(status_url):
    status_id = str(status_url.split("/")[-1].split("?")[0])
    show_api_url = "https://api.twitter.com/1.1/statuses/show.json"
    if token == "":
        print("No Token")
        return None
    headers = {"Authorization": "Bearer " + token}
    params = {
        "id": status_id,
        "tweet_mode": "extended"
    }
    res = requests.get(show_api_url, headers=headers, params=params)
    video_data = json.loads(res.text)
    try:
        video_data = json.loads(res.text)['extended_entities']['media'][0]['video_info']['variants']
        bitrate = [i["bitrate"] for i in video_data if i.get("bitrate")]
        bitrate = max(bitrate)
        for v in video_data:
            if "bitrate" in v:
                if v["bitrate"] == bitrate:
                    return v["url"]
    except BaseException:
        return None


def main():
    # global token
    # token = getToken()
    url = "https://twitter.com/nhk_sunnysideup/status/1172880002028888065"
    vurl = getVideoURL(url)
    print(vurl)


if __name__ == "__main__":
    main()
