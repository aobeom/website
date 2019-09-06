# coding=utf-8
import base64
import os
import re
import shutil
import tempfile
from multiprocessing.dummy import Pool

import requests

from modules.config import get_media_path_conf

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36",
}


session = requests.Session()
session.headers.update(headers)

auth1_api = "https://radiko.jp/v2/api/auth1"
auth2_api = "https://radiko.jp/v2/api/auth2"
playlist_api = "https://radiko.jp/v2/api/ts/playlist.m3u8"


def get_aac_urls(station_id, start_at, end_at):
    print("[1] Start")
    # auth1
    header_auth1 = {}
    header_auth1["x-radiko-device"] = "pc"
    header_auth1["x-radiko-user"] = "dummy_user"
    header_auth1["x-radiko-app"] = "pc_html5"
    header_auth1["x-radiko-app-version"] = "0.0.1"
    auth1_res = session.get(auth1_api, headers=header_auth1)
    authtoken = auth1_res.headers["X-Radiko-AuthToken"]
    offset = auth1_res.headers["X-Radiko-KeyOffset"]
    length = auth1_res.headers["X-Radiko-KeyLength"]

    # key
    # player_url = "http://radiko.jp/apps/js/playerCommon.js"
    # player_text = session.get(player_url).read()
    # key_rule = re.compile(r'new RadikoJSPlayer\(\$audio\[0\], \'pc_html5\', \'(.*?)\', {')
    # authkey = key_rule.findall(player_text, re.S | re.M)[0]
    authkey = "bcd151073c03b352e1ef2fd66c32209da9ca0afa"
    authkey = authkey.encode(encoding='utf-8')
    with tempfile.TemporaryFile() as temp:
        temp.write(authkey)
        temp.seek(int(offset))
        buff = temp.read(int(length))
        partialkey = base64.b64encode(buff)

    # auth2
    header_auth2 = {}
    header_auth2["x-radiko-device"] = "pc"
    header_auth2["x-radiko-user"] = "dummy_user"
    header_auth2["x-radiko-authtoken"] = authtoken
    header_auth2["x-radiko-partialkey"] = partialkey
    auth2_res = session.get(auth2_api, headers=header_auth2)

    area = auth2_res.text.split(",")[0]
    # playlist
    header_play = {}
    header_play["X-Radiko-AreaId"] = area
    header_play["X-Radiko-AuthToken"] = authtoken

    play_params = {
        "station_id": station_id,
        "start_at": start_at,
        "ft": start_at,
        "end_at": end_at,
        "to": end_at,
        "l": "15",
        "type": "b"
    }
    m3u8_list_res = session.get(playlist_api, params=play_params, headers=header_play)

    ip_status = m3u8_list_res.status_code
    print("[2] Check IP Address...")
    if ip_status == 200:
        m3u8_content = m3u8_list_res.text
        chunk_rule = r'http[s]?://.*?m3u8'
        m3u8_main_url_list = re.findall(chunk_rule, m3u8_content, re.S | re.M)
        m3u8_main_url = m3u8_main_url_list[0]
        media_rule = r'(http[s]?://.*?aac)'
        m3u8_main_res = session.get(m3u8_main_url)
        m3u8_main_content = m3u8_main_res.text
        aac_urls = re.findall(media_rule, m3u8_main_content, re.S | re.M)
        return aac_urls
    else:
        yourip = session.get("http://whatismyip.akamai.com/").text
        err_msg = {'YourIP': yourip, 'YourArea': area}
        print(err_msg)
        return None


def __core(para):
    url = para[0]
    filename = para[1]
    r = session.get(url)
    with open(filename, "wb") as code:
        for chunk in r.iter_content(chunk_size=1024):
            code.write(chunk)


def download(urls, aac_save_path):
    print("[3] Downloading...")
    tmpdir = tempfile.mkdtemp(prefix="radiko_")
    tmp_path = [os.path.join(tmpdir, str(index).zfill(8) + ".aac") for index, _ in enumerate(urls)]
    pool = Pool(4)
    pool.map(__core, zip(urls, tmp_path))
    pool.close()
    pool.join()
    videoin = ' '.join([os.path.join(tmpdir, _) for _ in tmp_path])
    os.system("cat " + videoin + " >" + aac_save_path)
    shutil.rmtree(tmpdir)


def get(file_name, station, start_at, end_at):
    urls = get_aac_urls(station, start_at, end_at)
    media_path = get_media_path_conf()['media_path']
    aac_save_path = os.path.join(media_path, file_name)
    if urls:
        download(urls, aac_save_path)
        return aac_save_path
    return None
