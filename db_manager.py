from db_connector import DBConnector


class DBManager(object):

    def __init__(self):
        self.db = DBConnector()
        self.collection = self.db.collection_fancuk

    def get_user_info(self, user_id):
        return self.collection.member.find_one({'user_id': user_id})

    def get_user_list(self):
        return self.collection.member.find()

    def add_user_info(self, request):
        return self.collection.member.insert_one({'user_id': request[0],
                                                  'user_pwd': request[1],
                                                  'name': request[2],
                                                  'student_id': request[3],
                                                  'grade': request[4],
                                                  'semester': request[5],
                                                  'phone': request[6],
                                                  'email': request[7],
                                                  'level': 1})

    def edit_user(self, request):
        return self.collection.member.update_one({'user_id': request[0]},
                                                 {'$set':
                                                     {
                                                         'name': request[1],
                                                         'student_id': request[2],
                                                         'grade': request[3],
                                                         'semester': request[4],
                                                         'level': request[5]
                                                     }})

    def reset_pwd(self, request, user_pwd):
        return self.collection.member.update_one({'user_id': request},
                                                 {'$set': {'user_pwd': user_pwd}})

    def count_elements(self, collection):
        return self.collection[collection].count()

    def add_library(self, request):
        return self.collection.library.insert_one({'title': request[0], 'writer': request[1],
                                                   'count': request[2], 'renter': [], 'image': request[3]})

    def get_library(self, page):
        return self.collection.library.find().limit(10).skip((page - 1) * 10)

    def rent_library(self, request, date, count):
        return self.collection.library.update_one({'title': request[0]},
                                                  {'$push': {'renter': {'user_id': request[1], 'date': date}},
                                                   '$set': {'count': count - 1}})

    def delete_library(self, request):
        return self.collection.library.delete_one({'title': request[0]})

    def find_library(self, title):
        return self.collection.library.find_one({'title': title})

    def return_library(self, request, count):
        return self.collection.library.update_one({'title': request[0]},
                                                  {'$pull': {'renter': {'user_id': request[1]}},
                                                   '$set': {'count': count + 1}})

    def edit_library(self, request):
        return self.collection.library.update_one({'title': request[0]},
                                                  {'$set':
                                                       {'title': request[1],
                                                        'writer': request[2],
                                                        'count': request[3],
                                                        'image': request[4]
                                                        }})

    def search_library(self, request):
        return self.collection.library.find({'title': {"$regex": request[0], "$options": 'm'}})

    def edit_user_profile(self, request):
        return self.collection.member.update_one({'user_id': request[0]},
                                                 {'$set':
                                                      {'user_pwd': request[1],
                                                       'name': request[2],
                                                       'student_id': request[3],
                                                       'grade': request[4],
                                                       'semester': request[5],
                                                       'phone': request[6],
                                                       'email': request[7]
                                                       }})

    def get_user_library(self, user_id):
        return self.collection.library.find({'renter': {'$elemMatch': {'user_id': user_id}}})

    def delete_user(self, user_id):
        return self.collection.member.delete_one({'user_id': user_id})

    def edit_user_level(self, user_id, level):
        return self.collection.member.update_one({'user_id': user_id},
                                                 {'$set':
                                                     {
                                                         'level': level
                                                     }
                                                 })

    def board_create(self, request):
        check = None
        if request[0] in self.collection.list_collection_names():
            return check
        else:
            self.collection[request[0]].insert_one({
                'title': '', 'writer': '', 'content': '', 'date': ''
            })
            return self.collection[request[0]].delete_one({'title': ''})

    def board_delete(self, request):
        return self.collection[request[0]].drop()

    def board_edit(self, request):
        return self.collection[request[0]].rename(request[1])

    def add_post(self, request, date):
        check = None
        if request[0] in self.collection.list_collection_names():
            check = self.collection[request[0]].insert_one({
                'title': request[1], 'writer': request[2], 'content': request[3], 'date': date
            })
            if check is not None:
                return check
        return check

    def get_posts(self, request):
        return self.collection[request[0]].find()

    def delete_post(self, request):
        return self.collection[request[0]].delete_one({'title': request[1], 'writer': request[2], 'date': request[3]})

    def get_detail_post(self, request):
        return self.collection[request[0]].find_one({'title': request[1], 'writer': request[2], 'date': request[3]})

    def edit_post(self, request):
        return self.collection[request[0]].update_one({'title': request[1], 'writer': request[2], 'date': request[3]},
                                                      {'$set':
                                                          {
                                                              'title': request[4],
                                                              'content': request[5]
                                                          }})

    def get_token(self, user_id):
        return self.collection.token.find_one({'user_id': user_id})

    def find_token(self, token):
        return self.collection.token.find_one({'token': token})

    def set_token(self, user_id, token, expired_time):
        return self.collection.token.insert_one({'user_id': user_id, 'token': token, 'time': expired_time})

    def recreate_token(self, user_id, token, expired_time):
        return self.collection.token.update_one({'user_id': user_id}, {'$set': {'token': token, 'time': expired_time}})

    def update_token(self, token, expired_time):
        return self.collection.token.update_one({'token': token}, {'$set': {'time': expired_time}})

    def expired_token(self, token, expired_time):
        return self.collection.token.update_one({'token': token}, {'$set': {'time': expired_time}})

    def __del__(self):
        pass
