# import re
import requests
import json
from lxml import etree


def getVideoURL(status_url):
    headers = {
        "User-Agent": "Mozilla/5.0 (iPad; CPU OS 11_0 like Mac OS X) AppleWebKit/604.1.34 (KHTML, like Gecko) Version/11.0 Mobile/15A5341f Safari/604.1"
    }
    headers_normal = headers.copy()
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

    # api_url = "https://api.twitter.com/2/timeline/conversation/{}.json?tweet_mode=extended".format(status_id)
    api_url = "https://api.twitter.com/2/timeline/conversation/{}.json".format(status_id)
    params = {
        "include_profile_interstitial_type": 1,
        "include_blocking": 1,
        "include_blocked_by": 1,
        "include_followed_by": 1,
        "include_want_retweets": 1,
        "include_mute_edge": 1,
        "include_can_dm": 1,
        "include_can_media_tag": 1,
        "skip_status": 1,
        "cards_platform": "Web-12",
        "include_cards": 1,
        "include_composer_source": True,
        "include_ext_alt_text": True,
        "include_reply_count": 1,
        "tweet_mode": "extended",
        "include_entities": True,
        "include_user_entities": True,
        "include_ext_media_color": True,
        "include_ext_media_availability": True,
        "send_error_codes": True,
        "count": 20,
        "ext": "mediaStats%2ChighlightedLabel%2CcameraMoment"
    }
    res = request.get(api_url, params=params, headers={'authorization': authorization, 'x-guest-token': guest_token})

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
        vmap_url = api_content['globalObjects']['tweets'][status_id]['card']['binding_values']['player_url']['string_value']
        res = requests.get(vmap_url, headers=headers_normal)
        tree = etree.fromstring(bytes(res.text, encoding='utf-8'))
        namespaces = {'tw': 'http://twitter.com/schema/videoVMapV2.xsd'}
        root = tree.xpath("//tw:videoVariant", namespaces=namespaces)
        video_bit_rate = [int(_.attrib.get("bit_rate")) for _ in root if _.attrib.get("content_type") == "video/mp4"]
        video_max_rate = max(video_bit_rate)
        for v in root:
            if v.attrib.get("bit_rate") == str(video_max_rate):
                return requests.utils.unquote(v.attrib.get("url"))


def main():
    url = "https://twitter.com/Umabi_Official/status/1130292055538896896"
    url = "https://twitter.com/kinglrg_/status/1129059497132068867"
    x = getVideoURL(url)
    print(x)


if __name__ == "__main__":
    main()
