from db_connector import DBConnector


class DBManager(object):

    def __init__(self):
        self.db = DBConnector()
        self.collection = self.db.collection_fancuk

    def get_user_info(self, id):
        return self.collection.member.find_one({"id": id})

    def add_library(self, title, writer, count):
        return self.collection.library.insert_one({"title": title, "writer": writer, "count": count, "renter": ""})

    def get_library(self):
        return self.collection.library.find()

    def edit_user_profile(self, json_request):
        return self.collection.member.update_one({'id': json_request['id']},
                                            {'$set':
                                                 {'pwd': json_request['pwd'],
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
