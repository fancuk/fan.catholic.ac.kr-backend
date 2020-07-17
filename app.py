import json

from flask import Flask, jsonify, request
from flask_request_validator import (Param, JSON, GET, Pattern, validate_params)
from db_manager import DBMannager
from bson.json_util import dumps
from bson import ObjectId, json_util

app = Flask(__name__)
mongo = DBMannager()


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/api/login', methods=['POST'])
def login():
    user_id = request.json['id']
    user_pwd = request.json['pwd']

    user_info = mongo.get_user_info(user_id)
    if user_info is not None:
        if user_pwd == user_info['password']:
            json_request = {'login': 'True'}
        else:
            json_request = {'login': 'False'}
    else:
        json_request = {'login': 'False'}

    return jsonify(json_request)


@app.route('/api/library/add' , methods=['POST'])
def add_library():
    title = request.json['title']
    writer = request.json['writer']
    count = request.json['count']
    check = mongo.add_library(title , writer, count)

    if check is not None:
        json_request = {'add' : 'True'}
    else:
        json_request = {'add' : 'False'}

    return jsonify(json_request)


@app.route('/api/library/list', methods=['GET'])
def list_library():
    check = mongo.get_library()

    if check is None:
        return {'list' : 'False'}

    docs = []
    for doc in check:
        doc.pop('_id') #개소름
        docs.append(doc)
    return jsonify(docs)


if __name__ == '__main__':
    app.run()
