import os
import sys
import time

import pymongo
from pymongo import DESCENDING

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.dirname(os.path.split(curPath)[0])
sys.path.append(rootPath)

from modules.config import get_mongo_conf

conf = get_mongo_conf()
dbhost = conf["dbhost"]
dbport = conf["dbport"]
# dbuser = conf["dbuser"]
dbname = conf["dbname"]

db_updatetime = "crond_time"
db_drama_info = "drama_info"
db_stchannel_info = "st_info"
db_stchannel_token = "st_token"
db_rika_info = "rikaMsg"


def dbCreator():
    db_connect = pymongo.MongoClient("mongodb://{}:{}/".format(dbhost, dbport), maxPoolSize=None)
    db_clinet = db_connect[dbname]
    return db_clinet


def updateTime(db_client, type_, time_):
    col = db_client[db_updatetime]
    query = {"type": type_}
    para = {'$set': {"time": time_}}
    col.update(query, para, True)


class dbDrama(object):
    def __init__(self, db_client):
        col = db_client[db_drama_info]
        self.quarter = self.__quarter_gen()
        self.mongo = col

    def __unifyTime(website, date):
        if website == "tvbt":
            struct_time = time.strptime(date, "%m%d")
        elif website == "subpig":
            struct_time = time.strptime(date, "%m/%d")
        return time.strftime("%m%d", struct_time)

    def __quarter_gen(self):
        year_month = time.strftime('%Y-%m', time.localtime(time.time()))
        year = year_month.split("-")[0]
        month = year_month.split("-")[-1]
        season = ""
        if month in ["01", "02", "03"]:
            season = "winter"
        elif month in ["04", "05", "06"]:
            season = "spring"
        elif month in ["07", "08", "09"]:
            season = "summer"
        elif month in ["10", "11", "12"]:
            season = "autumn"
        return year, season

    def update(self, website, data):
        for d in data:
            title = d["title"]
            url = d["url"]
            dlurls = d["dlurls"]
            if d.get("date"):
                date = self.__unifyTime(website, d["date"])
            else:
                date = "-"
            year = self.quarter[0]
            season = self.quarter[1]
            query = {
                "type": website,
                "url": url,
                "year": year,
                "season": season,
                "url": url,
            }
            para = {'$set': {"title": title, "date": date, "dlurls": dlurls}}
            upsert = True
            self.mongo.update(query, para, upsert=upsert)


class dbSTchannel(object):
    def __init__(self, db_client):
        col_info = db_client[db_stchannel_info]
        col_token = db_client[db_stchannel_token]
        self.col_info = col_info
        self.col_token = col_token

    def get_token(self):
        query = {}
        result = self.col_token.find_one(query)
        return result

    def refresh_token(self, token):
        query = {"token": token}
        para = {'$set': {"token": token}}
        upsert = True
        self.col_token.update(query, para, upsert)

    def updateMovieList(self, new_data):
        old_data = self.col_info.find({}, projection={'_id': False}).sort("date", DESCENDING).limit(15)
        diff_data = set.difference(*[{d['murl'] for d in diff} for diff in [new_data, old_data]])
        update_data = [d for d in new_data if d['murl'] in diff_data]
        return update_data

    def updateData(self, data):
        for d in data:
            title = d["title"]
            date = d["date"]
            murl = d["murl"]
            purl = d["purl"]
            query = {
                "purl": purl,
            }
            para = {'$set': {"title": title, "date": date, "murl": murl}}
            upsert = True
            self.col_info.update(query, para, upsert=upsert)

    def updateMoviePath(self, purl, path):
        query = {
            "purl": purl,
        }
        para = {'$set': {"path": path}}
        self.col_info.update(query, para)


class dbRikaMsg(object):
    def __init__(self, db_client):
        col = db_client[db_rika_info]
        self.mongo = col

    def checkInfo(self, tid):
        query = {
            "tid": tid
        }
        query = self.mongo.find(query).count()
        if query == 0:
            return True

    def update(self, query):
        self.mongo.insert_one(query)
