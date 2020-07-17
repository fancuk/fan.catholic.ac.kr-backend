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

    def __del__(self):
        mongo.close()
