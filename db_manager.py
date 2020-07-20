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
        return self.collection.member.update_one({'id': json_request[0]},
                                                 {'$set':
                                                      {'pwd': json_request[1],
                                                       'name': json_request[2],
                                                       'student_id': json_request[3],
                                                       'grade': json_request[4],
                                                       'semester': json_request[5],
                                                       'phone': json_request[6],
                                                       'email': json_request[7],
                                                       'level': json_request[8]
                                                       }})

    def __del__(self):
        pass
