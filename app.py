from flask import Flask, jsonify, request
from flask_request_validator import (Param, JSON, GET, Pattern, validate_params)
from db_manager import DBMannager


app = Flask(__name__)
mongo = DBMannager()

@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/api/login', methods=['POST'])
def login():
    user_id = request.json['id']
    user_pwd = request.json['pwd']
    check_id = mongo.get_user_info(user_id)

    if check_id is not None:
        if user_pwd == check_id['password']:
            json_request = {'login': 'True'}
        else:
            json_request = {'login': 'False'}
    else:
        json_request = {'login': 'False'}

    return jsonify(json_request)


if __name__ == '__main__':
    app.run()
