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
from data.barbers import Barber
from forms.login_user_form import LoginForm
from forms.record_user_form import RecordForm
from forms.register_barber_form import RegisterBarberForm
from forms.register_user_form import RegisterUserForm
from help_functions.for_map import search_address, getImage

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
    if not current_user.is_authenticated:
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
    else:
        return render_template('error_already_login.html', title='Уже зашел')


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    if not current_user.is_authenticated:
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
    else:
        return render_template('error_already_register.html', title='Уже зарегистрирован')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/book', methods=['GET', 'POST'])
@login_required
def book():
    form = RecordForm()

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


@app.route('/usercard', methods=['GET'])
@login_required
def usercard():
    db_sess = db_session.create_session()

    record = db_sess.query(Record).filter(Record.user_id == current_user.id).first()

    if record:
        user_record = f"Ваша последняя запись в {record.date_time}"
    else:
        user_record = "У вас нет записей"

    return render_template('usercard.html', user=current_user, user_record=user_record)


@app.route('/register_barber', methods=['GET', 'POST'])
@login_required
def register_barber():
    try:
        if current_user.id == 1:
            form = RegisterBarberForm()
            if form.validate_on_submit():
                if form.password.data != form.password_again.data:
                    return render_template('register_barber.html', title='Регистрация',
                                           form=form,
                                           message="Пароли не совпадают")
                db_sess = db_session.create_session()
                if db_sess.query(Barber).filter(Barber.email == form.email.data).first():
                    return render_template('register_barber.html', title='Регистрация',
                                           form=form,
                                           message="Такой пользователь уже есть")
                try:
                    barber = Barber(
                        email=form.email.data,
                        surname=form.surname.data,
                        name=form.name.data,
                        address=form.address,
                        city_from=form.city_from
                    )
                    barber.set_password(form.password.data)
                    db_sess.add(barber)
                    db_sess.commit()
                    return redirect('/login')
                except Exception as e:
                    print(e)
                    return 'Oops, something dont work'
            return render_template('register_barber.html', title='Регистрация', form=form)
        else:
            return render_template('error_403.html', title='Error 403')
    except Exception:
        return render_template('error_500.html', title='Error 500')


@app.route('/location', methods=['GET', 'POST'])
def location():
    res = search_address('Тверской бул., 24, стр. 1')
    link = getImage(res)
    return render_template('location.html', link=link)

@app.route('/barbers', methods=['GET', 'POST'])
def barbers():
    return render_template('error_500.html', title='Error 500')




if __name__ == '__main__':
    db_session.global_init("db/beatyweb.db")
    app.run(port=8080, host='127.0.0.1')
