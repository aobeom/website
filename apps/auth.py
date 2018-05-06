# -*- coding: utf-8 -*-
# @author AoBeom
# @create date 2018-04-07 19:35:33
# @modify date 2018-04-07 19:35:33
# @desc [auth]
import hashlib
from flask import redirect, render_template, request
from flask_login import login_user, logout_user

# mysql
# from model import User
# from apps import app, db

# mongodb
from model import User
from apps import app, mongo


API_VERSION = "/v1"
API_LOGIN = API_VERSION + "/api/login"
API_LOGOUT = API_VERSION + "/api/logout"


def md5(text):
    m = hashlib.md5()
    t = text.encode(encoding="utf-8")
    m.update(t)
    return m.hexdigest()


@app.route('/ulogin')
def login():
    return render_template("single_login.html")


# mysql
# @app.route(API_LOGIN, methods=['POST'], strict_slashes=False)
# def login_api():
#     user = request.form['user']
#     password = request.form['password']
#     un_vaild = User.query.filter_by(user=user).first()
#     pd_vaild = User.query.filter_by(password=md5(password)).first()
#     if un_vaild and pd_vaild:
#         login_user(un_vaild, True)
#         return redirect("/upload")
#     return redirect("/ulogin")

# mongodb
@app.route(API_LOGIN, methods=['POST'], strict_slashes=False)
def login_api():
    user = request.form['user']
    password = request.form['password']
    pd_vaild = mongo.db.users.find_one(
        {"user": user, "password": md5(password)})
    if pd_vaild:
        user_obj = User(pd_vaild['user'])
        login_user(user_obj, True)
        return redirect("/rika")
    return redirect("/ulogin")


@app.route(API_LOGOUT, methods=['POST'], strict_slashes=False)
def logout_api():
    logout_user()
    return redirect("/ulogin")
