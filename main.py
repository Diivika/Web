import os
from flask import Flask, url_for, request, render_template, redirect, abort, jsonify
import json
from flask import make_response
from requests import get
from flask_login import LoginManager, login_user
from flask_login import login_required, logout_user, current_user
from flask_restful import reqparse, abort, Api, Resource
from data import db_session



db_session.global_init("db/beatyweb.db")
db_sess = db_session.create_session()
app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


if __name__ == '__main__':
    db_session.global_init("db/beatyweb.db")
    app.run(port=8080, host='127.0.0.1')