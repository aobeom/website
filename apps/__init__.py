import sys
import os
sys.path.append("/usr/local/lib/python2.7/site-packages")
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from flask import Flask
from flask_httpauth import HTTPTokenAuth
from get_config import get_db_conf
from flask_restful import Api
# from flask_cors import CORS
# mysql
from flask_sqlalchemy import SQLAlchemy


conf = get_db_conf()
dbhost = conf["dbhost"]
dbport = conf["dbport"]
dbuser = conf["dbuser"]
dbpasswd = conf["dbpasswd"]
dbname = conf["dbname"]
secret_key = conf["secret_key"]

app = Flask(__name__, template_folder="../templates",
            static_folder='../static',)
app.config['SECRET_KEY'] = secret_key
api = Api(app, catch_all_404s=True)
# CORS(app, supports_credentials=True)
# mysql
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://{dbuser}:{dbpasswd}@{dbhost}:{dbport}/{dbname}'.format(
    dbuser=dbuser, dbpasswd=dbpasswd, dbhost=dbhost, dbport=dbport, dbname=dbname)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy()
db.init_app(app)

authen = HTTPTokenAuth(scheme='Bearer')

from apps import views, manager
