# coding: utf-8
from flask import Flask
from modules.config import get_mongo_conf, get_key
from flask_pymongo import PyMongo
from flask_httpauth import HTTPTokenAuth
from flask_restful import Api

# from flask_cors import CORS


conf = get_mongo_conf()
dbhost = conf["dbhost"]
dbport = conf["dbport"]
# dbuser = conf["dbuser"]
# dbpasswd = conf["dbpasswd"]
dbname = conf["dbname"]
if dbhost == "":
    dbhost = "127.0.0.1"
if dbport == "":
    dbport = "27017"
if dbname == "":
    print(" * MongoDB Info: No database selected in mongodb.conf")
    exit()

mongo_info = 'mongodb://{dbhost}:{dbport}/{dbname}'.format(dbhost=dbhost, dbport=dbport, dbname=dbname)
print(" * MongoDB Info: {}".format(mongo_info))


app = Flask(__name__, template_folder="../templates", static_folder='../static',)
app.config['SECRET_KEY'] = get_key()

# Mongodb
app.config.update(
    MONGO_URI='mongodb://{dbhost}:{dbport}/{dbname}'.format(
        dbhost=dbhost, dbport=dbport, dbname=dbname),
)

authen = HTTPTokenAuth(scheme='Bearer')
api = Api(app, catch_all_404s=True)
mongo = PyMongo(app, connect=False)

# CORS(app, supports_credentials=True)
