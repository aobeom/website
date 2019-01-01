# @author AoBeom
# @create date 2018-12-30 18:38:17
# @modify date 2019-01-01 10:34:29
# @desc [mongo]
import os
import sys
import time
import datetime
import base64
from passlib.hash import md5_crypt

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)

from modules.mongoMode import mongoMode

mongo = mongoMode()

db_users = "users"
db_user_token = "user_token"
db_updatetime = "crond_time"
db_media_info = "media_info"
db_live_info = "live_info"
db_drama_info = "drama_info"
db_stchannel_info = "st_info"
db_stchannel_token = "st_token"
db_program_info = "program_info"
db_rika_info = "rikaMsg"


def updateTime(type_, time_):
    mongo.mongoCol(db_updatetime)
    query = {"type": type_}
    para = {'$set': {"time": time_}}
    mongo.mongoUpdate(query, para, True)


class dbCrond(object):
    def getData(self, type_):
        mongo.mongoCol(db_updatetime)
        query = {
            "type": type_
        }
        data = mongo.mongoFindOne(query)
        return data


class dbAuth(object):
    def __init__(self):
        self.__setLiveTTL(604800)
        self.password = None

    def register(self, username, password):
        mongo.mongoCol(db_users)
        hash_pwd = self.__hash_password(password)
        query = {
            "username": username,
            "password": hash_pwd
        }
        user_check = mongo.mongoFindOne({"username": username})
        if user_check:
            return False
        else:
            mongo.mongoInsert(query)
            return True

    def login(self, username, password):
        mongo.mongoCol(db_users)
        query = {"username": username}
        hash_pwd = mongo.mongoFindOne(query)["password"]
        pwd_check = self.__verify_password(password, hash_pwd)
        if pwd_check:
            mongo.mongoCol(db_user_token)
            query = {
                "username": username,
            }
            db_token = mongo.mongoFindOne(query)
            if db_token:
                token = db_token["token"]
            else:
                token = self.__generate_token(username, password)
                self.__updateToken(username, token)
            return token
        else:
            return False

    def logout(self, username):
        mongo.mongoCol(db_users)
        query = {
            "username": username,
        }
        para = {'$set': {"token": ""}}
        mongo.mongoUpdate(query, para)
        return True

    def checkToken(self, token):
        mongo.mongoCol(db_user_token)
        query = {
            "token": token,
        }
        check = mongo.mongoFindOne(query)
        if check:
            username = check["username"]
            return username
        else:
            return False

    def __updateToken(self, username, token):
        mongo.mongoCol(db_user_token)
        query = {
            "username": username,
        }
        para = {'$set': {"token": token, "created_at": datetime.datetime.utcnow()}}
        upsert = True
        mongo.mongoUpdate(query, para, upsert)

    def __setLiveTTL(self, expire):
        mongo.mongoCol(db_user_token)
        index_check = mongo.mongoIndexInfo()
        if not index_check.get("created_at_1"):
            mongo.mongoIndex("created_at", expire)

    def __hash_password(self, pwd):
        password = md5_crypt.hash(pwd)
        return password

    def __generate_token(self, user, pwd):
        token = md5_crypt.encrypt(user + pwd)
        t_base64 = base64.b64encode(token.encode('utf-8'))
        t_base64 = str(t_base64, encoding="utf-8")
        return t_base64

    def __verify_password(self, pwd, hash_pwd):
        return md5_crypt.verify(pwd, hash_pwd)


class dbMedia(object):
    def __init__(self):
        pass

    def update(self, type_, website, url, source):
        mongo.mongoCol(db_media_info)
        query = {
            "type": type_,
            "website": website,
            "url": url,
            "source": source
        }
        mongo.mongoInsert(query)

    def getData(self, url):
        mongo.mongoCol(db_media_info)
        query = {
            "url": url
        }
        data = mongo.mongoFindOne(query)
        if data:
            return data
        else:
            return None

    def updateLive(self, type_, website, url, source):
        mongo.mongoCol(db_live_info)
        query = {
            "type": type_,
            "website": website,
            "url": url,
            "source": source,
            "created_at": datetime.datetime.utcnow()
        }
        mongo.mongoInsert(query)

    def getLiveData(self, url):
        mongo.mongoCol(db_live_info)
        query = {
            "url": url
        }
        data = mongo.mongoFindOne(query)
        if data:
            return data
        else:
            return None

    def setLiveTTL(self, expire):
        mongo.mongoCol(db_live_info)
        index_check = mongo.mongoIndexInfo()
        if not index_check.get("created_at_1"):
            mongo.mongoIndex("created_at", expire)


class dbDrama(object):
    def __init__(self):
        self.quarter = self.__quarter_gen()

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
        mongo.mongoCol(db_drama_info)
        for d in data:
            title = d["title"]
            url = d["url"]
            dlurls = d["dlurls"]
            if d.get("date"):
                date = d["date"]
            else:
                date = "0000"
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
            mongo.mongoUpdate(query, para, upsert)

    def getData(self, website):
        mongo.mongoCol(db_drama_info)
        query = {
            "type": website,
            "year": self.quarter[0],
            "season": self.quarter[1]
        }
        data = mongo.mongoFind(query)
        data = list(data)
        if len(data) != 0:
            return data
        else:
            return None


class dbProgram(object):
    def update(self, kw, ac, yahoo_url, prog_info):
        mongo.mongoCol(db_program_info)
        query = {
            "keyword": kw,
            "area_code": ac,
            "yahoo_url": yahoo_url,
            "prog_info": prog_info,
            "created_at": datetime.datetime.utcnow()
        }
        mongo.mongoInsert(query)

    def getData(self, kw, ac):
        mongo.mongoCol(db_program_info)
        query = {
            "keyword": kw,
            "area_code": ac
        }
        data = mongo.mongoFindOne(query)
        if data:
            return data
        else:
            return None

    def setTTL(self, expire):
        mongo.mongoCol(db_program_info)
        index_check = mongo.mongoIndexInfo()
        if not index_check.get("created_at_1"):
            mongo.mongoIndex("created_at", expire)


class dbSTchannel(object):
    def __init__(self):
        pass

    def get_token(self):
        mongo.mongoCol(db_stchannel_token)
        query = {}
        result = mongo.mongoFindOne(query)
        return result

    def refresh_token(self, token):
        mongo.mongoCol(db_stchannel_token)
        query = {"token": token}
        para = {'$set': {"token": token}}
        upsert = True
        mongo.mongoUpdate(query, para, upsert)

    def top15(self):
        mongo.mongoCol(db_stchannel_info)
        result = mongo.mongoFindLimit(15, sort=True, field="date", desc=True)
        return result

    def updateMovieList(self, new_data):
        mongo.mongoCol(db_stchannel_info)
        old_data = mongo.mongoFindLimit(15)
        diff_data = set.difference(*[{d['murl'] for d in diff} for diff in [new_data, old_data]])
        update_data = [d for d in new_data if d['murl'] in diff_data]
        return update_data

    def updateData(self, data):
        mongo.mongoCol(db_stchannel_info)
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
            mongo.mongoUpdate(query, para, upsert)

    def updateMoviePath(self, purl, path):
        mongo.mongoCol(db_stchannel_info)
        query = {
            "purl": purl,
        }
        para = {'$set': {"path": path}}
        mongo.mongoUpdate(query, para)


class dbRikaMsg(object):
    def getType(self, type_):
        mtype = {
            0: "Text",
            1: "Image",
            2: "Video",
            3: "Audio"
        }
        info = mtype.get(type_)
        return info

    def getPages(self, flag):
        mongo.mongoCol(db_rika_info)
        if flag == 100:
            count = mongo.mongoCount()
        elif flag in range(4):
            query = {
                "type": flag
            }
            count = mongo.mongoCount(query)
        else:
            count = 0
        comp = count % 10
        if comp != 0:
            pages = count // 10 + 1
        else:
            pages = count // 10
        return pages

    def getPageInfo(self, page, type_=None):
        mongo.mongoCol(db_rika_info)
        page = int(page)
        if page < 0:
            return None
        if type_ is not None:
            type_ = {
                "type": int(type_)
            }
        else:
            type_ = {}
        agr = [
            {'$match': type_},
            {'$project': {"_id": False}},
            {'$sort': {"date": -1}},
            {'$limit': 10}
        ]
        if page > 1:
            skip = {'$skip': 10 * (page - 1)}
            agr.insert(3, skip)
            result = mongo.mongoAggregate(agr)
        else:
            result = mongo.mongoAggregate(agr)
        result = list(result)
        return result

    def checkInfo(self, tid):
        mongo.mongoCol(db_rika_info)
        query = {
            "tid": tid
        }
        query = mongo.mongoCount(query)
        if query == 0:
            return True

    def update(self, query):
        mongo.mongoCol(db_rika_info)
        mongo.mongoInsert(query)
