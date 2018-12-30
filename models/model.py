import base64

from passlib.hash import md5_crypt as hash_pwd

# mysql
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


# mysql
class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), unique=True)
    password = db.Column(db.String(64))

    def hash_password(self, pwd):
        self.password = hash_pwd.encrypt(pwd)

    def generate_token(self, user, pwd):
        token = hash_pwd.encrypt(user + pwd)
        t_base64 = base64.b64encode(token.encode('utf-8'))
        return t_base64

    def verify_password(self, pwd):
        return hash_pwd.verify(pwd, self.password)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False
