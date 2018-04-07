from flask import redirect
from flask_login import UserMixin
from apps import login_manger, db


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(64))


@login_manger.user_loader
def load_user(id):
    user = User.query.get(int(id))
    return user


@login_manger.unauthorized_handler
def unauthorized():
    return redirect("/ulogin")
