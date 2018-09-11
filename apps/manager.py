# -*- coding: utf-8 -*-
# @author AoBeom
# @create date 2018-04-07 19:35:33
# @modify date 2018-09-09 20:49:59
# @desc [auth]

from flask_restful import reqparse, Resource, abort

# mysql
from model import User
from apps import db, api, redisMode

redis = redisMode.redisMode()
APIVERSION = "/api/v1"


def handler(status, data, **other):
    d = {}
    d["status"] = status
    d["message"] = data
    d["data"] = other
    return d


class Register(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', required=True,
                            help="username is required")
        parser.add_argument('password', required=True,
                            help="password is required")
        args = parser.parse_args()
        username = args["username"]
        password = args["password"]
        if username is None or password is None:
            abort(400)
        if User.query.filter_by(username=username).first() is not None:
            abort(400)
        user = User(username=username)
        user.hash_password(password)
        db.session.add(user)
        db.session.commit()
        return (user.username)


class Token(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username')
        parser.add_argument('password')
        args = parser.parse_args()
        username = args["username"]
        password = args["password"]
        if username and password is not None:
            user = User.query.filter_by(username=username).first()
            if not user or not user.verify_password(password):
                return handler(1, "username or password invalid")
            token = user.generate_token(username, password)
            redis.redisSave(token, username, ex=1200)
        else:
            return handler(1, "username or password invalid")
        return handler(0, "Hello " + username, token=token)


class Logout(Resource):
    def post(self):
        pass


api.add_resource(Register, APIVERSION + '/auth/register')
api.add_resource(Token, APIVERSION + '/auth/token')
api.add_resource(Logout, APIVERSION + '/auth/logout')
