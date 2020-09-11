from db_connector import DBConnector


class DBManager(object):

    def __init__(self):
        self.db = DBConnector()
        self.collection = self.db.collection_fancuk

    def get_user_info(self, user_id):
        return self.collection.member.find_one({'user_id': user_id})

    def get_user_list(self):
        return self.collection.member.find()

    def add_user_info(self, json_request):
        return self.collection.member.insert_one({'user_id': json_request[0],
                                                  'user_pwd': json_request[1],
                                                  'name': json_request[2],
                                                  'student_id': json_request[3],
                                                  'grade': json_request[4],
                                                  'semester': json_request[5],
                                                  'phone': json_request[6],
                                                  'email': json_request[7],
                                                  'level': 1})

    def reset_pwd(self, json_request, user_pwd):
        return self.collection.member.update_one({'user_id': json_request},
                                                 {'$set': {'user_pwd': user_pwd}})

    def add_library(self, json_request):
        return self.collection.library.insert_one({'title': json_request[0], 'writer': json_request[1],
                                                   'count': json_request[2], 'renter': [], 'image': json_request[3]})

    def get_library(self, page):
        return self.collection.library.find().limit(10).skip((page-1)*10)

    def rent_library(self, title, renter, date, count):
        return self.collection.library.update_one({'title': title},
                                                  {'$push': {'renter': {'user_id': renter, 'date': date}},
                                                   '$set': {'count': count - 1}})

    def delete_library(self, title):
        return self.collection.library.delete_one({'title': title})

    def find_library(self, title):
        return self.collection.library.find_one({'title': title})

    def return_library(self, title, renter, count):
        return self.collection.library.update_one({'title': title},
                                                  {'$pull': {'renter': {'user_id': renter}},
                                                   '$set': {'count': count + 1}})

    def edit_library(self, json_request):
        return self.collection.library.update_one({'title': json_request[0]},
                                                  {'$set':
                                                       {'title': json_request[1],
                                                        'writer': json_request[2],
                                                        'count': json_request[3],
                                                        'image': json_request[4]
                                                        }})

    def edit_user_profile(self, json_request):
        return self.collection.member.update_one({'user_id': json_request[0]},
                                                 {'$set':
                                                      {'user_pwd': json_request[1],
                                                       'name': json_request[2],
                                                       'student_id': json_request[3],
                                                       'grade': json_request[4],
                                                       'semester': json_request[5],
                                                       'phone': json_request[6],
                                                       'email': json_request[7]
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

    def add_board(self, json_request, date):
        check = None
        if json_request[0] == 'freeBoard':
            check = self.collection.freeBoard.insert_one(
                {'title': json_request[1], 'writer': json_request[2], 'content': json_request[3], 'date': date})
        elif json_request[0] == 'noticeBoard':
            check = self.collection.noticeBoard.insert_one(
                {'title': json_request[1], 'writer': json_request[2], 'content': json_request[3], 'date': date})
        elif json_request[0] == 'studyBoard':
            check = self.collection.studyBoard.insert_one(
                {'title': json_request[1], 'writer': json_request[2], 'content': json_request[3], 'date': date})
        return check

    def get_board(self, json_request):
        if json_request[0] == 'freeBoard':
            return self.collection.freeBoard.find()
        elif json_request[0] == 'noticeBoard':
            return self.collection.noticeBoard.find()
        elif json_request[0] == 'studyBoard':
            return self.collection.studyBoard.find()
          
    def delete_board(self, board_name, title, writer, date):
        if board_name == 'freeBoard':
            return self.collection.freeBoard.delete_one({'title': title, 'writer': writer, 'date': date})
        elif board_name == 'noticeBoard':
            return self.collection.noticeBoard.delete_one({'title': title, 'writer': writer, 'date': date})
        elif board_name == 'studyBoard':
            return self.collection.studyBoard.delete_one({'title': title, 'writer': writer, 'date': date})

    def get_detail_board(self, board_name, title, writer, date):
        if board_name == 'freeBoard':
            return self.collection.freeBoard.find_one({'title': title, 'writer': writer, 'date': date})
        elif board_name == 'noticeBoard':
            return self.collection.noticeBoard.find_one({'title': title, 'writer': writer, 'date': date})
        elif board_name == 'studyBoard':
            return self.collection.studyBoard.find_one({'title': title, 'writer': writer, 'date': date})

    def edit_board(self, board_name, title, writer, date, edit_title, edit_content):
        if board_name == 'freeBoard':
            return self.collection.freeBoard.update_one({'title': title, 'writer': writer, 'date': date},
                                                        {'$set':
                                                             {
                                                                 'title': edit_title,
                                                                 'content': edit_content
                                                             }})
        elif board_name == 'noticeBoard':
            return self.collection.noticeBoard.update_one({'title': title, 'writer': writer, 'date': date},
                                                        {'$set':
                                                             {
                                                                 'title': edit_title,
                                                                 'content': edit_content
                                                             }})
        elif board_name == 'studyBoard':
            return self.collection.studyBoard.update_one({'title': title, 'writer': writer, 'date': date},
                                                        {'$set':
                                                             {
                                                                 'title': edit_title,
                                                                 'content': edit_content
                                                             }})

    def get_token(self, user_id):
        return self.collection.token.find_one({'user_id': user_id})

    def find_token(self, token):
        return self.collection.token.find_one({'token': token})

    def set_token(self, user_id, token, expired_time):
        return self.collection.token.insert_one({'user_id': user_id, 'token': token, 'time': expired_time})

    def update_token(self, user_id, token, expired_time):
        return self.collection.token.update_one({'user_id': user_id}, {'$set': {'token': token, 'time': expired_time}})

    def expired_token(self, token, expired_time):
        return self.collection.token.update_one({'token': token}, {'$set': {'time': expired_time}})

    def __del__(self):
        pass
