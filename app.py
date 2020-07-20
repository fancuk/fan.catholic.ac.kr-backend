from flask import Flask, jsonify, request
from flask_request_validator import (Param, JSON, GET, Pattern, validate_params)
from db_manager import DBManager
import time
app = Flask(__name__)
mongo = DBManager()


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/api/login', methods=['POST'])
@validate_params(
    Param('id', JSON, str, rules=[Pattern(r'^[a-z0-9]+$')], required=True), #소문자와 숫자만 가능
    Param('pwd', JSON, str, required=True)
)
def login(*args):
    user_id = args[0]
    user_pwd = args[1]

    user_info = mongo.get_user_info(user_id)
    if user_info is not None:
        if user_pwd == user_info['pwd']:
            json_request = {'login': 'True'}
        else:
            json_request = {'login': 'False'}
    else:
        json_request = {'login': 'False'}

    return jsonify(json_request)


@app.route('/api/register', methods=['POST'])
def register():
    check = mongo.add_user_info(request.json)
    if check is not None:
        json_request = {'register' : 'True'}
    else:
        json_request = {'register' : 'False'}

    return jsonify(json_request)


@app.route('/api/library/add', methods=['POST'])
def add_library():
    title = request.json['title']
    writer = request.json['writer']
    count = request.json['count']
    image = request.json['image']
    check = mongo.add_library(title, writer, count, image)

    if check is not None:
        json_request = {'add': 'True'}
    else:
        json_request = {'add': 'False'}

    return jsonify(json_request)


@app.route('/api/library/list', methods=['GET'])
def list_library():
    check = mongo.get_library()

    if check is None:
        return {'list': 'False'}

    docs = []
    for doc in check:
        doc.pop('_id') #개소름
        docs.append(doc)
    return jsonify(docs)


@app.route('/api/library/rent', methods=['POST'])
def rent_library():
    title = request.json['title']
    renter = request.json['renter']
    find_library = mongo.find_library(title)
    count = find_library['count']
    print(count)
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


@app.route('/api/library/delete', methods=['POST'])
def delete_library():
    title = request.json['title']
    check = mongo.delete_library(title)
    if check is not None:
        json_request = {'delete': 'True'}
    else:
        json_request = {'delete': 'False'}
    return jsonify(json_request)


@app.route ('/api/profile/edit', methods=['POST'])
def edit_profile():
    check = mongo.edit_user_profile(request.json)
    if check is not None:
        return {'edit': 'True'}
    else:
        return {'edit': 'False'}


if __name__ == '__main__':
    app.run()
