from flask import redirect

# mysql
# from flask_login import UserMixin
# from apps import login_manger, db

# mongodb
from apps import login_manger, mongo

# mysql
# class User(db.Model, UserMixin):
#     __tablename__ = 'users'
#     id = db.Column(db.Integer, primary_key=True)
#     user = db.Column(db.String(20), unique=True)
#     password = db.Column(db.String(64))

# @login_manger.user_loader
# def load_user(id):
#     user = User.query.get(int(id))
#     return user


# mongodb
class User():
    def __init__(self, user):
        self.user = user

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.user


@login_manger.user_loader
def load_user(user):
    u = mongo.db.users.find_one({"user": user})
    if not u:
        return None
    return User(u['user'])


# common
@login_manger.unauthorized_handler
def unauthorized():
    return redirect("/ulogin")
