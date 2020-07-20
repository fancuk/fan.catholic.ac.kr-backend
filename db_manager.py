from db_connector import DBConnector

db = DBConnector()

class DBMannager:

    def __init__(self):
        pass

    def get_user_info(self, id):
        collection = db.mongo.login
        return collection.login.find_one({"id": id})

    def add_library(self, title, writer, count):
        collection = db.mongo.library
        return collection.book.insert_one({"title": title, "writer": writer, "count": count, "renter": ""})

    def get_library(self):
        collection = db.mongo.library
        return collection.book.find()

    def edit_user_profile(self, json_request):
        collection = db.mongo.Member_List
        return collection.test_collection.update_one({'id': json_request['id']},
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
        pass
