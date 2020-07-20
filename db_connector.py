from pymongo import MongoClient


class DBConnector(object):

    def __init__(self):
        db_id = "admin"
        db_passwd = "admin"
        self.mongo = MongoClient('mongodb://%s:%s@127.0.0.1:27017' % (db_id, db_passwd))


    def __del__(self):
        self.mongo.close()