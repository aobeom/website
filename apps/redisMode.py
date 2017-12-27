# -*- coding: utf-8 -*-
# @author AoBeom
# @create date 2017-12-22 09:48:50
# @modify date 2017-12-22 09:48:50
# @desc [py-redis简单封装]

import hashlib

import redis


class redisMode(object):
    def __init__(self):
        self.conn = redis.StrictRedis(host='localhost', port=6379, db=0)

    def __status(self):
        try:
            self.conn.info()
        except Exception as e:
            raise e

    def __hashMd5(self, value):
        md5 = hashlib.md5(value).hexdigest()[8:-8]
        return md5

    def redisCheck(self, keyname, md5value=False):
        self.__status()
        if md5value:
            keyname = self.__hashMd5(keyname)
        keys = self.conn.keys()
        if keyname in keys:
            value = self.conn.get(keyname)
            return value
        else:
            return None

    def redisList(self, value):
        value = list(eval(value))
        return value

    def redisDict(self, value):
        value = dict(eval(value))
        return value

    def redisSave(self, keyname, value, ex=2592000, md5value=False):
        self.__status()
        if md5value:
            keyname = self.__hashMd5(keyname)
        self.conn.set(keyname, value, ex=ex)
