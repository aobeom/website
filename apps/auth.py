# -*- coding: utf-8 -*-
# @author AoBeom
# @create date 2018-04-07 19:35:33
# @modify date 2018-12-30 18:37:46
# @desc [auth]
from flask_restful import reqparse, Resource


from modules import mongoSet
from apps import api
from modules.config import handler, get_key

secret_key = get_key()

User = mongoSet.dbAuth()

APIVERSION = "/api/v1"


class Register(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', required=True,
                            help="username is required")
        parser.add_argument('password', required=True,
                            help="password is required")
        parser.add_argument('flag')
        args = parser.parse_args()
        username = args["username"]
        password = args["password"]
        flag = args["flag"]
        if flag == secret_key:
            if username is None or password is None:
                return handler(1, "Username or Password Invalid")
            if User.register(username, password):
                return handler(0, "Dear " + username + " Welcome to API World!")
            else:
                return handler(1, "User already exists")
        else:
            return handler(1, "Permission denied")


class Token(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username')
        parser.add_argument('password')
        args = parser.parse_args()
        username = args["username"]
        password = args["password"]
        if username and password is not None:
            token = User.login(username, password)
            if not token:
                return handler(1, "username or password invalid")
        else:
            return handler(1, "username or password invalid")
        return handler(0, "Hello " + username, token=token)


class Logout(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username')
        args = parser.parse_args()
        username = args["username"]
        User.logout(username)
        return handler(0, "GoodBye " + username)


api.add_resource(Register, APIVERSION + '/auth/register')
api.add_resource(Token, APIVERSION + '/auth/token')
api.add_resource(Logout, APIVERSION + '/auth/logout')
