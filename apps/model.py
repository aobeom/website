from flask import redirect

# mysql
from flask_login import UserMixin
from apps import login_manger, db

from passlib.hash import md5_crypt as hash_pwd


# mysql
class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), unique=True)
    password = db.Column(db.String(64))

    def hash_password(self, pwd):
        self.password = hash_pwd.encrypt(pwd)

    def verify_password(self, pwd):
        return hash_pwd.verify(pwd, self.password)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False


@login_manger.user_loader
def load_user(id):
    return User.query.get(int(id))


# common
@login_manger.unauthorized_handler
def unauthorized():
    return redirect("/ulogin")
