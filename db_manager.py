from db_connector import DBConnector


class DBManager(object):

    def __init__(self):
        self.db = DBConnector()
        self.collection = self.db.collection_fancuk

    def get_user_info(self, id):
        return self.collection.member.find_one({"id": id})

    def add_user_info(self, json_request):
        return self.collection.member.insert_one({'id': json_request['id'],
                                                  'pwd': json_request['pwd'],
                                                  'name': json_request['name'],
                                                  'student_id': json_request['student_id'],
                                                  'grade': json_request['grade'],
                                                  'semester': json_request['semester'],
                                                  'phone': json_request['phone'],
                                                  'email': json_request['email'],
                                                  'level': 1})

    def add_library(self, json_request):
        return self.collection.library.insert_one({"title": json_request[0], "writer": json_request[1],
                                                   "count": json_request[2], "renter": [], "image": json_request[3]})

    def get_library(self):
        return self.collection.library.find()

    def rent_library(self, title, renter, date, count):
        return self.collection.library.update_one({'title': title},
                                                  {'$push': {'renter': {'user_id': renter, 'date': date}},
                                                   '$set': {'count': count-1}})

    def delete_library(self, title):
        return self.collection.library.delete_one({'title': title})

    def find_library(self, title):
        return self.collection.library.find_one({'title': title})

    def return_library(self, title, renter, count):
        return self.collection.library.update_one({'title': title},
                                                  {'$pull': {'renter': {'user_id': renter}},
                                                   '$set': {'count': count+1}})

    def edit_library(self, json_request):
        return self.collection.library.update_one({'title': json_request[0]},
                                                  {'$set':
                                                       {'count': json_request[1],
                                                        'image': json_request[2]
                                                        }})

    def edit_user_profile(self, json_request):
        return self.collection.member.update_one({'id': json_request[0]},
                                            {'$set':
                                                 {'pwd': json_request[1],
                                                  'name': json_request[2],
                                                  'student_id': json_request[3],
                                                  'grade': json_request[4],
                                                  'semester': json_request[5],
                                                  'phone': json_request[6],
                                                  'email': json_request[7]
                                                  }})

    def get_user_library(self, user_id):
        return self.collection.library.find({'renter': {'$elemMatch': {'user_id': user_id}}})

    def __del__(self):
        pass