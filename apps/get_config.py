import json
import os

work_dir = os.path.dirname(os.path.abspath(__file__))
dbconf = os.path.join(work_dir, "db.conf")


def getconf():
    f = open(dbconf, "rb")
    conf = json.loads(f.read())
    return conf
