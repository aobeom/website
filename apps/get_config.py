import json
import os

work_dir = os.path.dirname(os.path.abspath(__file__))
dbconf = os.path.join(work_dir, "db.conf")
mongoconf = os.path.join(work_dir, "mongodb.conf")
rikaconf = os.path.join(work_dir, "rikainfo.conf")
redisconf = os.path.join(work_dir, "redis.conf")


def __json_conf(conf):
    f = open(conf, "rb")
    conf = f.read()
    conf = json.loads(conf)
    f.close()
    return conf


def get_db_conf():
    return __json_conf(dbconf)


def get_rika_conf():
    return __json_conf(rikaconf)


def get_redis_conf():
    return __json_conf(redisconf)


def get_mongo_conf():
    return __json_conf(mongoconf)
