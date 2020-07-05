from flask import Flask, jsonify
from flask_request_validator import (Param, JSON, GET, Pattern, validate_params)

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
