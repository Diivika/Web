import os
from flask import Flask, url_for, request, render_template, redirect, abort, jsonify, flash
import json
from flask import make_response
from requests import get
from flask_login import LoginManager, login_user
from flask_login import login_required, logout_user, current_user
from flask_restful import reqparse, abort, Api, Resource
from data import db_session
from data.users import User
from forms.book_form import BookingForm
from data.records import Record
from data.category import Category



db_session.global_init("db/beatyweb.db")
db_sess = db_session.create_session()
app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.get(User, user_id)

@app.route('/')
def index():

    return render_template('home.html')



@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


if __name__ == '__main__':
    db_session.global_init("db/beatyweb.db")
    app.run(port=8080, host='127.0.0.1')