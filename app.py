from flask import Flask, jsonify, request, make_response
from flask_request_validator import (Param, JSON, GET, Pattern, validate_params)
from flask_cors import CORS
from db_manager import DBManager
from authentication import Authentication
import time

app = Flask(__name__)
CORS(app)
mongo = DBManager()
auth = Authentication()
token = None


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/api/login', methods=['POST'])
@validate_params(
    Param('user_id', JSON, str, rules=[Pattern(r'^[a-z0-9]+$')], required=True),  # 소문자와 숫자만 가능
    Param('user_pwd', JSON, str, required=True)
)
def login(*request_elements):
    user_id = request_elements[0]
    user_pwd = request_elements[1]
    user_info = mongo.get_user_info(user_id)
    if user_info is not None:
        if user_pwd == user_info['user_pwd']:
            auth.token_recreation(user_id)
            json_request = {'login': 'True', 'user_id': user_id, 'level': user_info['level'],
                            'token': auth.token_get(user_id)}
            resp = make_response(json_request)
            resp.headers['Authorization'] = auth.token_get(user_id)
            return resp
        else:
            json_request = {'login': False}
    else:
        json_request = {'login': False}

    return jsonify(json_request)


@app.route('/api/check/id', methods=['GET'])
@validate_params(
    Param('user_id', GET, str, rules=[Pattern(r'^[a-z0-9]+$')], required=True),  # 소문자와 숫자만 가능
)
def check_id(*request_elements):
    check = mongo.get_user_info(request_elements[0])
    if check is None:
        return {'id': True}
    return {'id': False}


@app.route('/api/logout', methods=['GET'])
@validate_params(
    Param('user_id', GET, str, rules=[Pattern(r'^.{1,50}$')], required=True)
)
def logout(*request_elements):
    if auth.token_expired(request_elements[0]).modified_count == 1:
        return {'logout': True}
    else:
        return {'logout': False}


@app.route('/api/register', methods=['POST'])
@validate_params(
    Param('user_id', JSON, str, rules=[Pattern(r'^[a-z0-9]+$')], required=True),  # 소문자와 숫자만 가능
    Param('user_pwd', JSON, str, required=True),
    Param('name', JSON, str, rules=[Pattern(r'^[가-힣]*$')], required=True),
    Param('student_id', JSON, str, rules=[Pattern(r'^[0-9]+$')], required=True),
    Param('grade', JSON, str, rules=[Pattern(r'\d')], required=True),
    Param('semester', JSON, str, rules=[Pattern(r'\d')], required=True),
    Param('phone', JSON, str, rules=[Pattern(r'\d{2,3}-\d{3,4}-\d{4}')], required=True),
    Param('email', JSON, str, rules=[Pattern(r'[a-zA-Z0-9_-]+@[a-z]+.[a-z]+')], required=True)
)
def register(*request_elements):
    check = mongo.get_user_info(request_elements[0])
    if check is None:
        check = mongo.add_user_info(request_elements)
        if check is not None:
            auth.token_creation(request_elements[0])
            json_request = {'register': True}
        else:
            json_request = {'register': False}
    else:
        json_request = {'register': False}

    return jsonify(json_request)


@app.route('/api/reset/pwd', methods=['PUT'])
@validate_params(
    Param('user_id', JSON, str, rules=[Pattern(r'^[a-z0-9]+$')], required=True)  # 소문자와 숫자만 가능
)
def reset_pwd(*request_elements):
    token = request.headers.get('Authorization')
    if token is not None:
        check = auth.token_update(token).modified_count
        if check != 0:
            if mongo.get_user_info(auth.id_get(token))['level'] == '3':
                user_pwd = 'fancuk'
                mongo.reset_pwd(request_elements[0], user_pwd)
                return {'reset': True}
    return {'token': False}


@app.route('/api/library/add', methods=['POST'])
@validate_params(
    Param('title', JSON, str, rules=[Pattern(r'^.{1,30}$')], required=True),
    Param('writer', JSON, str, rules=[Pattern(r'^.{2,30}$')], required=True),
    Param('count', JSON, str, rules=[Pattern(r'\d')], required=True),
    Param('image', JSON, str, rules=[Pattern(r'^.{5,100000}$')], required=True)
)
def add_library(*request_elements):
    token = request.headers.get('Authorization')
    if token is not None:
        check = auth.token_update(token).modified_count
        if check != 0:
            if mongo.get_user_info(auth.id_get(token))['level'] == '3':
                overlap = mongo.find_library(request_elements[0])
                if overlap is None:
                    check = mongo.add_library(request_elements)
                    if check is not None:
                        json_request = {'add': True}
                    else:
                        json_request = {'add': False}

                    return jsonify(json_request)
                else:
                    return jsonify(json_request={'error_code': 409, 'error_msg': '책 중복'})
    return {'token': False}


@app.route('/api/library/list', methods=['GET'])
@validate_params(
    Param('page', GET, str, rules=[Pattern(r'\d')], required=True)
)
def list_library(*request_elements):
    token = request.headers.get('Authorization')
    if token is not None:
        auth.token_update(token)
    page = request_elements[0]
    check = mongo.get_library(int(page))
    if check is None:
        return {'list': 'False'}

    docs = []
    for doc in check:
        doc.pop('_id')  # 개소름
        docs.append(doc)
    if int(mongo.count_elements('library') % 10) is 0:
        page = int(mongo.count_elements('library') / 10)
    else:
        page = int(mongo.count_elements('library') / 10) + 1
    book_list = {'books': docs}, {'page': page}
    return jsonify(book_list)


@app.route('/api/library/rent', methods=['POST'])
@validate_params(
    Param('title', JSON, str, rules=[Pattern(r'^.{1,30}$')], required=True)
)
def rent_library(*request_elements):
    token = request.headers.get('Authorization')
    if token is not None:
        check = auth.token_update(token).modified_count
        if check != 0:
            title = request_elements[0]
            renter = auth.id_get(token)
            find_library = mongo.find_library(title)
            count = int(find_library['count'])
            if count <= 0:
                json_request = {'rent': False}
            else:
                now = time.localtime()
                now_time = str(now.tm_year) + '-' + str(now.tm_mon) + '-' + str(now.tm_mday)
                check = mongo.rent_library(title, renter, now_time, count)
                if check is not None:
                    json_request = {'rent': True}
                else:
                    json_request = {'rent': False}
            return jsonify(json_request)
    return {'token': False}


@app.route('/api/library/delete', methods=['DELETE'])
@validate_params(
    Param('title', GET, str, rules=[Pattern(r'^.{1,30}$')], required=True)
)
def delete_library(*request_elements):
    token = request.headers.get('Authorization')
    if token is not None:
        check = auth.token_update(token).modified_count
        if check != 0:
            if mongo.get_user_info(auth.id_get(token))['level'] == '3':
                mongo.delete_library(request_elements)
                return {'delete': True}
    return {'token': False}


@app.route('/api/library/return', methods=['PUT'])
@validate_params(
    Param('title', JSON, str, rules=[Pattern(r'^.{1,30}$')], required=True)
)
def return_library(*request_elements):
    token = request.headers.get('Authorization')
    if token is not None:
        check = auth.token_update(token).modified_count
        if check != 0:
            title = request_elements[0]
            renter = auth.id_get(token)
            find_library = mongo.find_library(title)
            if find_library is not None:
                count = int(find_library['count'])
                check = mongo.return_library(title, renter, count)
                if check is not None:
                    return {'return': True}
            return {'return': False}
    return {'token': False}


@app.route('/api/library/edit', methods=['POST'])
@validate_params(
    Param('title', JSON, str, rules=[Pattern(r'^.{1,30}$')], required=True),
    Param('edit_title', JSON, str, rules=[Pattern(r'^.{1,30}$')], required=True),
    Param('edit_writer', JSON, str, rules=[Pattern(r'^.{2,30}$')], required=True),
    Param('edit_count', JSON, str, rules=[Pattern(r'\d')], required=True),
    Param('edit_image', JSON, str, rules=[Pattern(r'^.{5,100000}$')], required=True)
)
def edit_library(*request_elements):
    token = request.headers.get('Authorization')
    if token is not None:
        check = auth.token_update(token).modified_count
        if check != 0:
            if mongo.get_user_info(auth.id_get(token))['level'] == '3':
                check = mongo.edit_library(request_elements)
                if check is not None:
                    return {'edit': True}
                else:
                    return {'edit': False}
    return {'token': False}


@app.route('/api/library/search', methods=['GET'])
@validate_params(
    Param('title', GET, str, rules=[Pattern(r'^.{1,30}$')], required=True)
)
def search_library(*request_elements):
    check = mongo.search_library(request_elements)
    if check is None:
        return {'list': 'False'}

    docs = []
    for doc in check:  # 개소름
        doc.pop('_id')
        docs.append(doc)
    return jsonify(docs)


@app.route('/api/library/rent_list', methods=['GET'])
def rent_list_library(*request_elements):
    token = request.headers.get('Authorization')
    if token is not None:
        auth.token_update(token)
    check = mongo.get_library_all_list()
    if check is None:
        return {'list': 'False'}

    docs = []
    for doc in check:
        doc.pop('_id')  # 개소름
        if int(len(doc['renter'])) is not 0:
            docs.append(doc)

    if int(len(docs) % 10) is 0:
        page = int(len(docs) / 10)
    else:
        page = int(len(docs) / 10) + 1
    book_list = {'books': docs}, {'page': page}
    return jsonify(book_list)


@app.route('/api/profile/edit', methods=['PUT'])
@validate_params(
    Param('user_id', JSON, str, rules=[Pattern(r'^[a-z0-9]+$')], required=True),  # 소문자와 숫자만 가능
    Param('user_pwd', JSON, str, required=True),
    Param('name', JSON, str, rules=[Pattern(r'^[가-힣]*$')], required=True),
    Param('student_id', JSON, str, rules=[Pattern(r'^[0-9]+$')], required=True),
    Param('grade', JSON, str, rules=[Pattern(r'\d')], required=True),
    Param('semester', JSON, str, rules=[Pattern(r'\d')], required=True),
    Param('phone', JSON, str, rules=[Pattern(r'\d{2,3}-\d{3,4}-\d{4}')], required=True),
    Param('email', JSON, str, rules=[Pattern(r'[a-zA-Z0-9_-]+@[a-z]+.[a-z]+')], required=True)
)
def edit_profile(*request_elements):
    token = request.headers.get('Authorization')
    if token is not None:
        check = auth.token_update(token).modified_count
        if check != 0:
            if auth.id_get(token) == request_elements[0]:
                check = mongo.edit_user_profile(request_elements)
                if check is not None:
                    return {'edit': True}
                else:
                    return {'edit': False}
    return {'token': False}


@app.route('/api/profile/info', methods=['GET'])
@validate_params(
    Param('user_id', GET, str, rules=[Pattern(r'^[a-z0-9]+$')], required=True),  # 소문자와 숫자만 가능
)
def info_profile(*request_elements):
    token = request.headers.get('Authorization')
    if token is not None:
        check = auth.token_update(token).modified_count
        if check != 0:
            if auth.id_get(token) == request_elements[0]:
                check = mongo.get_user_info(request_elements[0])
                if check is not None:
                    check.pop('_id')
                    check.pop('user_pwd')
                    return check
    return {'token': False}


@app.route('/api/user/library', methods=['GET'])
@validate_params(
    Param('user_id', GET, str, rules=[Pattern(r'^[a-z0-9]+$')], required=True)
)
def my_library(*request_elements):
    token = request.headers.get('Authorization')
    if token is not None:
        check = auth.token_update(token).modified_count
        if check != 0:
            if auth.id_get(token) == request_elements[0]:
                check = mongo.get_user_library(request_elements[0])

                docs = []
                for doc in check:
                    doc.pop('_id')  # 개소름
                    docs.append(doc)
                return jsonify(docs)
    return {'token': False}


@app.route('/api/profile/drop', methods=['POST'])
@validate_params(
    Param('user_id', JSON, str, rules=[Pattern(r'^[a-z0-9]+$')], required=True),  # 소문자와 숫자만 가능
    Param('user_pwd', JSON, str, required=True)
)
def drop_user(*request_elements):
    token = request.headers.get('Authorization')
    if token is not None:
        check = auth.token_update(token).modified_count
        if check != 0:
            if auth.id_get(token) == request_elements[0]:
                user_id = request_elements[0]
                user_pwd = request_elements[1]
                user_info = mongo.get_user_info(user_id)
                if user_info is not None:
                    if user_pwd == user_info['user_pwd']:
                        auth.token_delete(user_id)
                        mongo.delete_user(user_id)
                        return {'delete': True}
                return {'delete': False}
    return {'token': False}


@app.route('/api/user/delete', methods=['DELETE'])
@validate_params(
    Param('user_id', GET, str, rules=[Pattern(r'^[a-z0-9]+$')], required=True)  # 소문자와 숫자만 가능
)
def delete_user(*request_elements):
    token = request.headers.get('Authorization')
    if token is not None:
        check = auth.token_update(token).modified_count
        if check != 0:
            if mongo.get_user_info(auth.id_get(token))['level'] == '3':
                user_id = request_elements[0]
                user_info = mongo.get_user_info(user_id)
                if user_info is not None:
                    auth.token_delete(user_id)
                    mongo.delete_user(user_id)
                    return {'delete': True}
                return {'delete': False}
    return {'token': False}


@app.route('/api/user/list', methods=['GET'])
def user_list():
    token = request.headers.get('Authorization')
    if token is not None:
        check = auth.token_update(token).modified_count
        if check != 0:
            check = mongo.get_user_list()
            docs = []
            for doc in check:
                doc.pop('_id')  # 개소름
                docs.append(doc)
            if check is not None:
                return jsonify(docs)
            else:
                return {'list': False}
    return {'token': False}


@app.route('/api/user/edit', methods=['PUT'])
@validate_params(
    Param('user_id', JSON, str, rules=[Pattern(r'^[a-z0-9]+$')], required=True),  # 소문자와 숫자만 가능
    Param('name', JSON, str, rules=[Pattern(r'^[가-힣]*$')], required=True),
    Param('student_id', JSON, str, rules=[Pattern(r'^[0-9]+$')], required=True),
    Param('grade', JSON, str, rules=[Pattern(r'\d')], required=True),
    Param('semester', JSON, str, rules=[Pattern(r'\d')], required=True),
    Param('level', JSON, str, rules=[Pattern(r'\d')], required=True)
)
def edit_user(*request_elements):
    token = request.headers.get('Authorization')
    if token is not None:
        check = auth.token_update(token).modified_count
        if check != 0:
            if mongo.get_user_info(auth.id_get(token))['level'] == '3':
                check = mongo.edit_user(request_elements)
                if check.modified_count != 0:
                    return {'edit': True}
                else:
                    return {'edit': False}
    return {'token': False}


@app.route('/api/board/create', methods=['POST'])
@validate_params(
    Param('board_name', JSON, str, rules=[Pattern(r'^.{1,30}$')], required=True)
)
def create_board(*request_elements):
    token = request.headers.get('Authorization')
    if token is not None:
        check = auth.token_update(token).modified_count
        if check != 0:
            if mongo.get_user_info(auth.id_get(token))['level'] == '3':
                check = mongo.board_create(request_elements)
                if check is None:
                    return {'create': False}
                return {'create': True}
    return {'token': False}


@app.route('/api/board/delete', methods=['DELETE'])
@validate_params(
    Param('board_name', GET, str, rules=[Pattern(r'^.{1,30}$')], required=True)
)
def delete_board(*request_elements):
    token = request.headers.get('Authorization')
    if token is not None:
        check = auth.token_update(token).modified_count
        if check != 0:
            if mongo.get_user_info(auth.id_get(token))['level'] == '3':
                mongo.board_delete(request_elements)
                return {'delete': True}
    return {'token': False}


@app.route('/api/board/edit', methods=['PUT'])
@validate_params(
    Param('board_name', JSON, str, rules=[Pattern(r'^.{1,30}$')], required=True),
    Param('edit_name', JSON, str, rules=[Pattern(r'^.{1,30}$')], required=True)
)
def edit_board(*request_elements):
    token = request.headers.get('Authorization')
    if token is not None:
        check = auth.token_update(token).modified_count
        if check != 0:
            if mongo.get_user_info(auth.id_get(token))['level'] == '3':
                mongo.board_edit(request_elements)
                return {'edit': True}
    return {'token': False}


@app.route('/api/post/add', methods=['POST'])
@validate_params(
    Param('board_name', JSON, str, rules=[Pattern(r'^.{1,30}$')], required=True),
    Param('title', JSON, str, rules=[Pattern(r'^.{1,30}$')], required=True),
    Param('writer', JSON, str, rules=[Pattern(r'^.{2,30}$')], required=True),
    Param('content', JSON, str, rules=[Pattern(r'^.{2,10000}$')], required=True)
)
def add_post(*request_elements):
    token = request.headers.get('Authorization')
    if token is not None:
        check = auth.token_update(token).modified_count
        if check != 0:
            now = time.localtime()
            now_time = str(now.tm_year) + '-' + str(now.tm_mon) + '-' + str(now.tm_mday)
            overlap = mongo.add_post(request_elements, now_time)
            if overlap is None:
                json_request = {'add': False}
            else:
                json_request = {'add': True}

            return jsonify(json_request)
    return {'token': False}


@app.route('/api/post/list', methods=['GET'])
@validate_params(
    Param('board_name', GET, str, rules=[Pattern(r'^.{1,30}$')], required=True),
    Param('page', GET, str, rules=[Pattern(r'\d')], required=False)
)
def list_post(*request_elements):
    token = request.headers.get('Authorization')
    if token is not None:
        check = auth.token_update(token).modified_count
        if check != 0:
            board_name = request_elements[0]

            if request_elements[1] is None:
                page = 1
            else:
                page = request_elements[1]
            check = mongo.get_posts(board_name, int(page))

            if check is None:
                return {'list': False}

            docs = []
            for doc in check:  # 개소름
                doc.pop('_id')
                docs.append(doc)

            if int(mongo.count_elements(board_name) % 10) is 0:
                page = int(mongo.count_elements(board_name) / 10)
            else:
                page = int(mongo.count_elements(board_name) / 10) + 1
            post_list = {'posts': docs}, {'page': page}

            return jsonify(post_list)
    return {'token': False}


@app.route('/api/post/delete', methods=['DELETE'])
@validate_params(
    Param('board_name', GET, str, rules=[Pattern(r'^.{1,30}$')], required=True),
    Param('title', GET, str, rules=[Pattern(r'^.{1,30}$')], required=True),
    Param('writer', GET, str, rules=[Pattern(r'^.{2,30}$')], required=True),
    Param('date', GET, str, rules=[Pattern(r'^.{2,30}$')], required=True)
)
def delete_post(*request_elements):
    token = request.headers.get('Authorization')
    if token is not None:
        check = auth.token_update(token).modified_count
        if check != 0:
            if auth.id_get(token) == request_elements[3]:
                mongo.delete_post(request_elements)
                return {'delete': True}
    return {'token': False}


@app.route('/api/post/detail', methods=['GET'])
@validate_params(
    Param('board_name', GET, str, rules=[Pattern(r'^.{1,30}$')], required=True),
    Param('title', GET, str, rules=[Pattern(r'^.{1,30}$')], required=True),
    Param('writer', GET, str, rules=[Pattern(r'^.{2,30}$')], required=True),
    Param('date', GET, str, rules=[Pattern(r'^.{2,30}$')], required=True)
)
def detail_post(*request_elements):
    token = request.headers.get('Authorization')
    if token is not None:
        check = auth.token_update(token).modified_count
        if check != 0:
            check = mongo.get_detail_post(request_elements)
            check.pop('_id')
            if check is None:
                return {'detail': False}
            else:
                return check
    return {'token': False}


@app.route('/api/post/edit', methods=['PUT'])
@validate_params(
    Param('board_name', JSON, str, rules=[Pattern(r'^.{1,30}$')], required=True),
    Param('title', JSON, str, rules=[Pattern(r'^.{1,30}$')], required=True),
    Param('writer', JSON, str, rules=[Pattern(r'^.{2,30}$')], required=True),
    Param('date', JSON, str, rules=[Pattern(r'^.{2,30}$')], required=True),
    Param('edit_title', JSON, str, rules=[Pattern(r'^.{1,30}$')], required=True),
    Param('edit_content', JSON, str, rules=[Pattern(r'^.{2,10000}$')], required=True),
)
def edit_post(*request_elements):
    token = request.headers.get('Authorization')
    if token is not None:
        check = auth.token_update(token).modified_count
        if check != 0:
            if auth.id_get(token) == request_elements[2]:
                check = mongo.edit_post(request_elements)
                if check.modified_count != 0:
                    return {'edit': True}
                else:
                    return {'edit': False}
    return {'token': False}


@app.route('/api/post/get_list', methods=['GET'])
@validate_params(
    Param('board_name', GET, str, rules=[Pattern(r'^.{1,30}$')], required=True),
    Param('count', GET, str, rules=[Pattern(r'\d')], required=True)
)
def get_list_post(*request_elements):
    token = request.headers.get('Authorization')
    if token is not None:
        check = auth.token_update(token).modified_count
        if check != 0:
            check = mongo.get_special_posts(request_elements)

            if check is None:
                return {'list': False}

            docs = []
            for doc in check:  # 개소름
                doc.pop('_id')
                docs.append(doc)

            return jsonify(docs)
    return {'token': False}


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
