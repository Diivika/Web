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
# from forms.book_form import BookingForm
from data.records import Record
from data.category import Category
from forms.login_user_form import LoginForm
from forms.record_user_form import RecordForm
from forms.register_user_form import RegisterUserForm

db_session.global_init("db/beatyweb.db")
db_sess = db_session.create_session()
app = Flask(__name__, template_folder='static/templates')
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


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterUserForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register_user.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register_user.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        try:
            user = User(
                email=form.email.data,
                surname=form.surname.data,
                name=form.name.data,
            )
            user.set_password(form.password.data)
            db_sess.add(user)
            db_sess.commit()
            return redirect('/login')
        except Exception as e:
            print(e)
            return 'Oops, something dont work'
    return render_template('register_user.html', title='Регистрация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/book', methods=['GET', 'POST'])
def book():
    form = RecordForm()

    if not current_user.is_authenticated:
        flash('Пожалуйста, зарегистрируйтесь или войдите, чтобы записаться', 'warning')
        return redirect(url_for('login'))

    db_sess = db_session.create_session()
    styles = db_sess.query(Category).all()

    if request.method == 'POST':
        try:
            record = Record(
                date_time=form.date.data,
                user_id=current_user.id,
            )
            db_sess.add(record)
            db_sess.commit()
            flash('Запись успешно создана!', 'success')
            return redirect('/')
        except Exception as e:
            db_sess.rollback()
            print(e)
            flash('Произошла ошибка при создании записи', 'danger')

    return render_template('record_user.html', title='Запись', form=form, styles=styles)


if __name__ == '__main__':
    db_session.global_init("db/beatyweb.db")
    app.run(port=8080, host='127.0.0.1')
