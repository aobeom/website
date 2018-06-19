# coding=utf-8
import json
import os
import time

import requests

import redisMode


def req(url, dl=False):
    headers = {
        "User-Agent": "com.ss.android.ugc.trill/247 (Linux; U; Android 7.1.1; ja_JP; E6533; Build/32.4.A.0.160; Cronet/58.0.2991.0)"
    }
    response = requests.get(url, headers=headers)
    return response


def videoInfo():
    api_url = "https://www.tiktokv.com/aweme/v1/aweme/post/?user_id=6543424280516263938&count=21&max_cursor=0&aid=1180&_signature="
    res = req(api_url).text
    api_info = json.loads(res)
    video_info = []
    for status in api_info["aweme_list"]:
        info_dict = {}
        t = time.strftime("%Y-%m-%d %H:%M:%S",
                          time.localtime(status["create_time"]))
        info_dict["time"] = t
        info_dict["playlist"] = status["video"]["play_addr"]["url_list"][0]
        info_dict["cover"] = status["video"]["cover"]["url_list"][0]
        info_dict["text"] = status["desc"]
        video_info.append(info_dict)
    return video_info


def videoDL(vinfo, path):
    if vinfo:
        for v in vinfo:
            v_url = v["playlist"]
            v_name = os.path.join(path, str(int(time.time())) + ".mp4")
            c_url = v["cover"]
            c_name = os.path.join(path, str(int(time.time())) + ".jpg")
            vres = req(v_url)
            with open(v_name, "wb") as code:
                for chunk in vres.iter_content(chunk_size=1024):
                    code.write(chunk)
            time.sleep(1)
            cres = req(c_url)
            with open(c_name, "wb") as code:
                for chunk in cres.iter_content(chunk_size=1024):
                    code.write(chunk)
    else:
        print("No update")


def newVideo(new, old):
    update = []
    for i in new:
        if i in old:
            continue
        else:
            update.append(i)
    return update


def main():
    path = os.path.dirname(os.path.abspath(__file__))
    times = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    r = redisMode.redisMode()
    redis_info = "tik:info"
    redis_utime = "tik:utime"
    vinfo_old = r.redisCheck(redis_info)
    vinfo = videoInfo()
    if vinfo_old:
        print "Update Checking..."
        vinfo_old = r.redisList(vinfo_old)
        update = newVideo(vinfo, vinfo_old)
        videoDL(update, path)
        r.redisSave(redis_info, vinfo)
        r.redisSave(redis_utime, times)
    else:
        print "First Download..."
        r.redisSave(redis_info, vinfo)
        r.redisSave(redis_utime, times)
        videoDL(vinfo, path)


if __name__ == "__main__":
    main()
