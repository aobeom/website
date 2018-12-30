# @author AoBeom
# @create date 2018-07-27 20:56:17
# @modify date 2018-12-30 16:15:36
# @desc [rika msg]
import json
import os
import sys
import time

import requests

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)

from modules.config import get_rika_conf
from modules import mongoSet

db = mongoSet.dbRikaMsg()


class rikaMsg(object):
    def __init__(self, crond=False):
        # rika auth
        rikaconf = get_rika_conf()
        self.username = rikaconf["username"]
        self.token = rikaconf["token"]
        self.group = rikaconf["group"]
        self.headers = {
            "X-API-Version": "1.4.0",
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 7.1.1; E6533 Build/32.4.A.0.160)",
        }

        # media path
        self.folder = "rika"
        work_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), ".."))
        self.save_path = os.path.join(work_dir, "media", self.folder)

    def keya_history(self, fromdate=None, todate=None, count=10, sortorder=0):
        # date format "2018/01/01 00:00:00"
        keya_msg = []
        url = "https://client-k.hot.sonydna.com/article/allhistory"
        headers = self.headers
        history_data = {
            "username": self.username,
            "token": self.token,
            "fromdate": fromdate,
            "todate": todate,
            "count": count,
            "sortorder": sortorder,
            "group": self.group
        }
        response = requests.post(url=url, headers=headers, json=history_data)
        keya_result = json.loads(response.text)
        data = keya_result["result"]["history"]
        total = str(len(data))
        print("Update {}".format(total))
        for d in data:
            keya_new_dict = {}
            keya_body = d["body"]
            nodata = db.checkInfo(keya_body["contents"])
            if nodata:
                keya_new_dict["tid"] = keya_body["contents"]
                keya_new_dict["text"] = keya_body["talk"]
                keya_new_dict["type"] = keya_body["media"]
                keya_new_dict["date"] = keya_body["date"]
                keya_msg.append(keya_new_dict)
            else:
                print("Already Exist")
                return None
        return keya_msg

    def keya_media(self, message=None):
        media = []
        url = "https://client-k.hot.sonydna.com/article"
        headers = self.headers
        media_data = {
            "username": self.username,
            "token": self.token
        }
        for m in message:
            keya_type = m["type"]
            if keya_type != 0:
                media_dict = {}
                media_data["article"] = m["tid"]
                response = requests.post(
                    url=url, headers=headers, json=media_data)
                keya_result = json.loads(response.text)
                media_url = keya_result["result"]["url"]
                media_dict["url"] = media_url
                media_dict["tid"] = m["tid"]
                media_dict["type"] = m["type"]
                media_dict["date"] = m["date"]
                media.append(media_dict)
        return media

    def keya_text(self, message):
        keya_word = []
        for msg in message:
            insert_record = {
                "date": msg["date"],
                "tid": msg["tid"],
                "type": msg["type"],
                "text": msg["text"],
                "media": ""
            }
            keya_word.append(insert_record)
            db.update(insert_record)
        return keya_word

    def keya_allmsg(self, message, media_info):
        keya_infos = []
        for msg in message:
            for mda in media_info:
                if msg["tid"] == mda["tid"]:
                    msg["media"] = mda["media"]
                    insert_record = {
                        "date": msg["date"],
                        "tid": msg["tid"],
                        "type": msg["type"],
                        "text": msg["text"],
                        "media": msg["media"]
                    }
                    break
                else:
                    msg["media"] = ""
                    insert_record = {
                        "date": msg["date"],
                        "tid": msg["tid"],
                        "type": msg["type"],
                        "text": msg["text"],
                        "media": msg["media"]
                    }
            db.update(insert_record)
            keya_infos.append(msg)
        return keya_infos

    def keya_download(self, media):
        media_info = []
        if not os.path.exists(self.save_path):
            os.mkdir(self.save_path)
        for m in media:
            media_dict = {}
            if m["type"] == 1:
                media_path = os.path.join(self.save_path, m["tid"] + ".jpg")
                media_uri = "/{}/{}".format(self.folder, m["tid"] + ".jpg")
            elif m["type"] == 2:
                media_path = os.path.join(self.save_path, m["tid"] + ".mp4")
                media_uri = "/{}/{}".format(self.folder, m["tid"] + ".mp4")
            elif m["type"] == 3:
                media_path = os.path.join(self.save_path, m["tid"] + ".m4a")
                media_uri = "/{}/{}".format(self.folder, m["tid"] + ".m4a")
            url = m["url"]
            media_dict["tid"] = m["tid"]
            media_dict["date"] = m["date"]
            media_dict["type"] = m["type"]
            media_dict["media"] = media_uri
            media_info.append(media_dict)
            r = requests.get(url, headers=self.headers,
                             stream=True, timeout=30)
            with open(media_path, "wb") as code:
                for chunk in r.iter_content(chunk_size=1024):
                    code.write(chunk)
        return media_info


def timeformat(timestamp):
    dformat = "%Y/%m/%d %H:%M:%S"
    value = time.localtime(timestamp)
    return time.strftime(dformat, value)


def main():
    msg = rikaMsg(crond=True)
    # fromdate = "2018/02/03 00:00:00"
    # todate = "2018/02/04 00:00:00"

    # crond
    end = time.time()
    start = end - 86400
    fromdate = timeformat(start)
    todate = timeformat(end)

    print("From {} to {}".format(fromdate, todate))
    keya_msg = msg.keya_history(fromdate, todate)
    if keya_msg:
        media_msg = msg.keya_media(keya_msg)
        if media_msg:
            media_info = msg.keya_download(media_msg)
            msg.keya_allmsg(keya_msg, media_info)
        else:
            msg.keya_text(keya_msg)
    else:
        print("No update")


if __name__ == "__main__":
    main()
