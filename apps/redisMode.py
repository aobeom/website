# -*- coding: utf-8 -*-
# @author AoBeom
# @create date 2017-12-22 09:48:50
# @modify date 2018-03-09 21:18:59
# @desc [py-redis简单封装]

import hashlib

import get_config
import redis


class redisMode(object):
    def __init__(self):
        redisconf = get_config.get_redis_conf()
        redis_host = redisconf["redis_host"]
        redis_port = redisconf["redis_port"]
        self.conn = redis.StrictRedis(host=redis_host, port=redis_port, db=0)

    def __status(self):
        try:
            self.conn.info()
        except Exception as e:
            raise e

    def __hashMd5(self, value):
        try:
            value = bytes(value, encoding="utf-8")
        except TypeError:
            value = value
        md5 = hashlib.md5(value).hexdigest()[8:-8]
        return md5

    def redisCheck(self, keyname, md5value=False, subkey=False):
        self.__status()
        if subkey:
            main_key = keyname.split(":")[0]
            sub_key = keyname.split(":")[-1]
            sub_key = self.__hashMd5(sub_key)
            keyname = "{}:{}".format(main_key, sub_key)
        if md5value:
            keyname = self.__hashMd5(keyname)
        if self.conn.exists(keyname):
            value = self.conn.get(keyname)
            try:
                value = str(value, encoding="utf-8")
            except TypeError:
                value = value
            return value
        else:
            return None

    def redisDel(self, keyname):
        self.__status()
        self.conn.delete(keyname)
        return None

    def redisList(self, value):
        value = list(eval(value))
        return value

    def redisDict(self, value):
        value = dict(eval(value))
        return value

    def redisKeys(self, prekey):
        self.__status()
        value = self.conn.keys(prekey)
        return value

    def redisSave(self, keyname, value, ex=2592000, md5value=False, subkey=False):
        self.__status()
        if subkey:
            main_key = keyname.split(":")[0]
            sub_key = keyname.split(":")[-1]
            sub_key = self.__hashMd5(sub_key)
            keyname = "{}:{}".format(main_key, sub_key)
        if md5value:
            keyname = self.__hashMd5(keyname)
        self.conn.set(keyname, value, ex=ex)

    def redisCounter(self, keyname, ex=10):
        self.__status()
        self.conn.incr(keyname)
        self.conn.expire(keyname, ex)

    def redisTTL(self, keyname):
        self.__status()
        ttl = self.conn.ttl(keyname)
        return ttl
