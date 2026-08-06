import flask.json
import flask
import json
if not hasattr(flask.json, 'JSONEncoder'):
    flask.json.JSONEncoder = json.JSONEncoder
if not hasattr(flask.Flask, 'json_encoder'):
    flask.Flask.json_encoder = json.JSONEncoder

from flask_mongoengine import MongoEngine
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
db = MongoEngine()
login_manager = LoginManager()
bcrypt = Bcrypt()