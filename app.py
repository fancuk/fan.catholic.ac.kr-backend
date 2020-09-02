from flask import Flask, jsonify, request
from flask_request_validator import (Param, JSON, GET, Pattern, validate_params)
from flask_cors import CORS
from db_manager import DBManager
import time

app = Flask(__name__)
CORS(app)
mongo = DBManager()


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/api/login', methods=['POST'])
@validate_params(
    Param('user_id', JSON, str, rules=[Pattern(r'^[a-z0-9]+$')], required=True),  # 소문자와 숫자만 가능
    Param('user_pwd', JSON, str, required=True)
)
def login(*args):
    user_id = args[0]
    user_pwd = args[1]
    user_info = mongo.get_user_info(user_id)
    if user_info is not None:
        if user_pwd == user_info['user_pwd']:
            json_request = {'user_id': user_id}
        else:
            json_request = {'login': 'False'}
    else:
        json_request = {'login': 'False'}

    return jsonify(json_request)


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
def register(*args):
    check = mongo.add_user_info(args)
    if check is not None:
        json_request = {'register': 'True'}
    else:
        json_request = {'register': 'False'}

    return jsonify(json_request)


@app.route('/api/reset/pwd', methods=['POST'])
@validate_params(
    Param('user_id', JSON, str, rules=[Pattern(r'^[a-z0-9]+$')], required=True)  # 소문자와 숫자만 가능
)
def reset_pwd(*args):
    user_pwd = 'fancuk'
    check = mongo.reset_pwd(args[0], user_pwd)
    return {'reset': 'True'}


@app.route('/api/library/add', methods=['POST'])
@validate_params(
    Param('title', JSON, str, rules=[Pattern(r'^.{1,30}$')], required=True),
    Param('writer', JSON, str, rules=[Pattern(r'^.{2,30}$')], required=True),
    Param('count', JSON, str, rules=[Pattern(r'\d')], required=True),
    Param('image', JSON, str, rules=[Pattern(r'^.{5,30}$')], required=True)
)
def add_library(*args):
    overlap = mongo.find_library(args[0])
    if overlap is None:
        check = mongo.add_library(args)
        if check is not None:
            json_request = {'add': 'True'}
        else:
            json_request = {'add': 'False'}

        return jsonify(json_request)
    else:
        return jsonify(json_request={'error_code': 409, 'error_msg': '책 중복'})


@app.route('/api/library/list', methods=['GET'])
def list_library():
    check = mongo.get_library()

    if check is None:
        return {'list': 'False'}

    docs = []
    for doc in check:
        doc.pop('_id')  # 개소름
        docs.append(doc)
    return jsonify(docs)


@app.route('/api/library/rent', methods=['POST'])
def rent_library():
    title = request.json['title']
    renter = request.json['renter']
    find_library = mongo.find_library(title)
    count = int(find_library['count'])
    if count <= 0:
        json_request = {'rent': 'False'}
    else:
        now = time.localtime()
        now_time = str(now.tm_year) + '-' + str(now.tm_mon) + '-' + str(now.tm_mday)
        check = mongo.rent_library(title, renter, now_time, count)
        if check is not None:
            json_request = {'rent': 'True'}
        else:
            json_request = {'rent': 'False'}

    return jsonify(json_request)


@app.route('/api/library/delete', methods=['DELETE'])
def delete_library():
    title = request.args.get('title')
    check = mongo.delete_library(title)
    return {'delete': 'True'}


@app.route('/api/library/return', methods=['PUT'])
def return_library():
    title = request.json['title']
    renter = request.json['renter']
    find_library = mongo.find_library(title)
    count = int(find_library['count'])
    check = mongo.return_library(title, renter, count)
    if check is not None:
        json_request = {'return': 'True'}
    else:
        json_request = {'return': 'False'}
    return jsonify(json_request)


@app.route('/api/library/edit', methods=['POST'])
@validate_params(
    Param('title', JSON, str, rules=[Pattern(r'^.{1,30}$')], required=True),
    Param('edit_count', JSON, str, rules=[Pattern(r'\d')], required=True),
    Param('edit_image', JSON, str, rules=[Pattern(r'^.{5,30}$')], required=True)
)
def edit_library(*args):
    check = mongo.edit_library(args)
    if check is not None:
        return {'edit': 'True'}
    else:
        return {'edit': 'False'}


@app.route('/api/profile/edit', methods=['PUT'])
@validate_params(
    Param('id', JSON, str, rules=[Pattern(r'^[a-z0-9]+$')], required=True),  # 소문자와 숫자만 가능
    Param('user_pwd', JSON, str, required=True),
    Param('name', JSON, str, rules=[Pattern(r'^[가-힣]*$')], required=True),
    Param('student_id', JSON, str, rules=[Pattern(r'^[0-9]+$')], required=True),
    Param('grade', JSON, str, rules=[Pattern(r'\d')], required=True),
    Param('semester', JSON, str, rules=[Pattern(r'\d')], required=True),
    Param('phone', JSON, str, rules=[Pattern(r'\d{2,3}-\d{3,4}-\d{4}')], required=True),
    Param('email', JSON, str, rules=[Pattern(r'[a-zA-Z0-9_-]+@[a-z]+.[a-z]+')], required=True)
)
def edit_profile(*args):
    check = mongo.edit_user_profile(args)
    if check is not None:
        return {'edit': 'True'}
    else:
        return {'edit': 'False'}


@app.route('/api/user/library', methods=['GET'])
def my_library():
    user_id = request.args.get('user_id')
    check = mongo.get_user_library(user_id)

    docs = []
    for doc in check:
        doc.pop('_id')  # 개소름
        docs.append(doc)
    return jsonify(docs)


@app.route('/api/delete/user', methods=['DELETE'])
def delete_user():
    user_id = request.args.get('user_id')
    check = mongo.delete_user(user_id)
    return {'delete': 'True'}


@app.route('/api/manage/edit', methods=['PUT'])
def edit_user_level():
    user_id = request.json['user_id']
    level = request.json['level']
    check = mongo.edit_user_level(user_id, level)
    if check is not None:
        return {'edit': 'True'}
    else:
        return {'edit': 'False'}


@app.route('/api/board/add', methods=['POST'])
@validate_params(
    Param('board_name', JSON, str, rules=[Pattern(r'^.{1,30}$')], required=True),
    Param('title', JSON, str, rules=[Pattern(r'^.{1,30}$')], required=True),
    Param('writer', JSON, str, rules=[Pattern(r'^.{2,30}$')], required=True),
    Param('content', JSON, str, rules=[Pattern(r'^.{2,30}$')], required=True)
)
def add_board(*args):
    now = time.localtime()
    now_time = str(now.tm_year) + '-' + str(now.tm_mon) + '-' + str(now.tm_mday)
    overlap = mongo.add_board(args, now_time)
    if overlap is None:
        json_request = {'add': 'False'}
    else:
        json_request = {'add': 'True'}

    return jsonify(json_request)
  
  
@app.route('/api/board/list', methods=['GET'])
@validate_params(
    Param('board_name', GET, str, rules=[Pattern(r'^.{1,30}$')], required=True)
)
def list_board(*args):
    board_name = request.args.get(args)
    check = mongo.get_board(args)

    if check is None:
        return {'list': 'False'}

    docs = []
    for doc in check:  # 개소름
        doc.pop('_id')
        docs.append(doc)
    return jsonify(docs)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
