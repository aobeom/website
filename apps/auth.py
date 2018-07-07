# -*- coding: utf-8 -*-
# @author AoBeom
# @create date 2018-04-07 19:35:33
# @modify date 2018-07-07 22:16:50
# @desc [auth]

from flask import redirect, render_template
from flask_login import login_user, logout_user
from flask_restful import reqparse, Resource, abort

# mysql
from model import User
from apps import app, db, api


APIVERSION = "/api/v1"


@app.route('/ulogin')
def login_index():
    return render_template("single_login.html")


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


class Login(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', required=True,
                            help="username is required")
        parser.add_argument('password', required=True,
                            help="password is required")
        args = parser.parse_args()
        username = args["username"]
        password = args["password"]
        user = User.query.filter_by(username=username).first()
        if not user or not user.verify_password(password):
            return redirect("/ulogin")
        login_user(user, True)
        return redirect("/rika")


class Logout(Resource):
    def post(self):
        logout_user()
        return redirect("/ulogin")


api.add_resource(Register, APIVERSION + '/register')
api.add_resource(Login, APIVERSION + '/login')
api.add_resource(Logout, APIVERSION + '/logout')
