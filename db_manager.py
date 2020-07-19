from pymongo import MongoClient

db_id = "admin"
db_passwd = "admin"
mongo = MongoClient('mongodb://%s:%s@127.0.0.1:27017' % (db_id, db_passwd))


class DBMannager:

    def __init__(self):
        pass

    def get_user_info(self, id):
        db = mongo.login
        return db.login.find_one({"id": id})

    def add_library(self, title, writer, count):
        db = mongo.library
        return db.book.insert_one({"title": title, "writer": writer, "count": count, "renter": ""})

    def get_library(self):
        db = mongo.library
        return db.book.find()

    def edit_user_profile(self, json_request):
        db = mongo.Member_List
        return db.test_collection.update_one({'id': json_request['id']},
                                             {'$set':
                                                  {'passward': json_request['pwd'],
                                                   'name': json_request['name'],
                                                   'student_id': json_request['student_id'],
                                                   'grade': json_request['grade'],
                                                   'semester': json_request['semester'],
                                                   'phone': json_request['phone'],
                                                   'email': json_request['email'],
                                                   'level': json_request['level']
                                                   }})

    def __del__(self):
        mongo.close()
