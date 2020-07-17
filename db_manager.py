from sqlite3.dbapi2 import Date

from pymongo import MongoClient
db_id = "admin"
db_pwd = "admin"
mongo = MongoClient('mongodb://%s:%s@localhost:27017' % (db_id, db_pwd))


class DBMannager:

    def __init__(self):
        pass

    def get_user_info(self, id):
        db = mongo.login
        return db.login.find_one({"id": id})


    def add_library(self, title, writer, count):
        db = mongo.library
        return db.book.insert_one({"title" : title, "writer" : writer, "count" : count, "renter" : ""})


    def get_library(self):
        db = mongo.library
        return db.book.find()


    def __del__(self):
        mongo.close()
