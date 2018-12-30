import json
import os

work_dir = os.path.dirname((os.path.dirname(os.path.abspath(__file__))))
mongoconf = os.path.join(work_dir, "configs", "mongodb.conf")
rikaconf = os.path.join(work_dir, "configs", "rikainfo.conf")
redisconf = os.path.join(work_dir, "configs", "redis.conf")
mediapath = os.path.join(work_dir, "configs", "mediapath.conf")
secret_key = "maruq"


def __json_conf(conf):
    with open(conf, "rb") as f:
        data = json.loads(f.read().decode("utf-8"))
    return data


def get_rika_conf():
    return __json_conf(rikaconf)


def get_redis_conf():
    return __json_conf(redisconf)


def get_mongo_conf():
    return __json_conf(mongoconf)


def get_media_path_conf():
    return __json_conf(mediapath)


def get_key():
    return secret_key


def handler(status, data, **other):
    d = {}
    d["status"] = status
    d["message"] = data
    d["data"] = other
    return d
