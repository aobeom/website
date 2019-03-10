# @author AoBeom
# @create date 2018-12-30 18:38:09
# @modify date 2019-03-10 11:23:04
# @desc [mongo]
from apps import mongo
from flask_pymongo import DESCENDING, ASCENDING


class mongoMode(object):
    def __init__(self):
        self.col = None

    def mongoCol(self, collection):
        self.col = getattr(mongo.db, collection)

    def mongoFind(self, query={}, sort=False, field="_id", desc=False, projection={'_id': False}):
        if sort:
            if desc:
                order = DESCENDING
            else:
                order = ASCENDING
            result = self.col.find(query, projection=projection).sort(field, order)
        else:
            result = self.col.find(query, projection=projection)
        return result

    def mongoFindOne(self, query={}, projection={'_id': False}):
        result = self.col.find_one(query, projection=projection)
        return result

    def mongoFindLimit(self, limit, sort=False, field="_id", desc=False, projection={'_id': False}):
        if sort:
            if desc:
                order = DESCENDING
            else:
                order = ASCENDING
            result = self.col.find({}, projection=projection).sort(field, order).limit(limit)
        else:
            result = self.col.find({}, projection=projection).sort(field, DESCENDING).limit(limit)
        return result

    def mongoCount(self, query={}):
        result = self.col.find(query).count()
        return result

    def mongoInsert(self, query):
        self.col.insert_one(query)

    def mongoUpdate(self, query, para, upsert=False):
        self.col.update_one(query, para, upsert=upsert)

    def mongoDelete(self, query):
        self.col.delete_one(query)

    def mongoIndex(self, query, expire=None):
        if expire:
            self.col.create_index(query, expireAfterSeconds=expire)
        else:
            self.col.create_index(query)

    def mongoIndexInfo(self):
        result = self.col.index_information()
        return result

    def mongoAggregate(self, agr):
        result = self.col.aggregate(agr)
        return result
