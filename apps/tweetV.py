# import re
import requests
import json


def getVideoURL(status_url):
    headers = {
        "User-Agent": "Mozilla/5.0 (iPad; CPU OS 11_0 like Mac OS X) AppleWebKit/604.1.34 (KHTML, like Gecko) Version/11.0 Mobile/15A5341f Safari/604.1"
    }
    request = requests.Session()
    request.headers.update(headers)
    status_id = str(status_url.split("/")[-1].split("?")[0])

    # Bearer
    # video_url = "https://twitter.com/i/videos/" + status_id
    # res = request.get(video_url)
    # html_content = res.text
    # js_url_rule = r'src="([^"]+)"'
    # js_url = ''.join(re.findall(js_url_rule, html_content))
    # js_res = request.get(js_url)
    # js_content = js_res.text
    # bearer_rule = r'"(Bearer [^"]+)"'
    # authorization = re.findall(bearer_rule, js_content, re.S | re.M)
    # authorization = ''.join(authorization)
    authorization = "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"

    guest_api_url = 'https://api.twitter.com/1.1/guest/activate.json'
    res = request.post(guest_api_url, headers={'authorization': authorization})
    guest_content = res.text
    guest_token = json.loads(guest_content)['guest_token']

    api_url = "https://api.twitter.com/2/timeline/conversation/{}.json?tweet_mode=extended".format(status_id)
    res = request.get(api_url, headers={'authorization': authorization, 'x-guest-token': guest_token})

    api_content = json.loads(res.text)
    try:
        variants = api_content['globalObjects']['tweets'][status_id]['extended_entities']['media'][0]['video_info']['variants']
        bitrate = [i["bitrate"] for i in variants if i.get("bitrate")]
        bitrate = max(bitrate)
        for v in variants:
            if "bitrate" in v:
                if v["bitrate"] == bitrate:
                    return v["url"]
    except BaseException:
        return None


def main():
    url = "https://mobile.twitter.com/Yukiriiiin__K/status/1072347909675540482"
    getVideoURL(url)


if __name__ == "__main__":
    main()
