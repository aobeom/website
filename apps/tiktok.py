# coding=utf-8
import requests
import time
import json
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


def videoDL(vinfo):
    for v in vinfo:
        v_url = v["playlist"]
        v_name = str(int(time.time())) + ".mp4"
        c_url = v["cover"]
        c_name = str(int(time.time())) + ".jpg"
        vres = req(v_url)
        with open(v_name, "wb") as code:
            for chunk in vres.iter_content(chunk_size=1024):
                code.write(chunk)
        time.sleep(1)
        cres = req(c_url)
        with open(c_name, "wb") as code:
            for chunk in cres.iter_content(chunk_size=1024):
                code.write(chunk)


def main():
    vinfo = videoInfo()
    r = redisMode.redisMode()
    r.redisSave("tiktok", vinfo)
    # videoDL(vinfo)


if __name__ == "__main__":
    main()
