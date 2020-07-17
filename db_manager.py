from pymongo import MongoClient
db_id = "taewan"
db_pwd = "1234"
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

    def __del__(self):
        mongo.close()
