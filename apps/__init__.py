from flask import Flask
from flask_login import LoginManager, login_manager
from flask_sqlalchemy import SQLAlchemy
from get_config import getconf

conf = getconf()
dbhost = conf["dbhost"]
dbport = conf["dbport"]
dbuser = conf["dbuser"]
dbpasswd = conf["dbpasswd"]
dbname = conf["dbname"]
secret_key = conf["secret_key"]

app = Flask(__name__, template_folder="../templates",
            static_folder='../static',)
app.config['SECRET_KEY'] = secret_key
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://{dbuser}:{dbpasswd}@{dbhost}:{dbport}/{dbname}'.format(
    dbuser=dbuser, dbpasswd=dbpasswd, dbhost=dbhost, dbport=dbport, dbname=dbname)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy()
db.init_app(app)
login_manger = LoginManager()
login_manger.session_protection = 'strong'
login_manager.login_view = 'auth.login'
login_manger.init_app(app)

from apps import views, auth
