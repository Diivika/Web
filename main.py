import datetime
import os
from pprint import pprint

from flask import Flask, url_for, request, render_template, redirect, abort, jsonify, flash
import json
from flask import make_response
from requests import get
from flask_login import LoginManager, login_user
from flask_login import login_required, logout_user, current_user
from flask_restful import reqparse, abort, Api, Resource
from werkzeug.utils import secure_filename

from data import db_session, barbers_api
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
    user = db_sess.query(Barber).filter(Barber.id == int(user_id)).first()
    if not user:
        user = db_sess.query(User).filter(User.id == int(user_id)).first()
    return user


@app.route('/')
def index():
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if not current_user.is_authenticated:
        form = LoginForm()
        if form.validate_on_submit():
            db_sess = db_session.create_session()
            user = db_sess.query(Barber).filter(Barber.email == form.email.data).first()
            if not user:
                user = db_sess.query(User).filter(User.email == form.email.data).first()
            if user and user.check_password(form.password.data):
                login_user(user, remember=form.remember_me.data)
                if user.is_barber:
                    return redirect(url_for('barber_card'))
                else:
                    return redirect(url_for('usercard'))
            flash('Неправильный логин или пароль', 'danger')
            return render_template('login.html', title='Авторизация', form=form)

        return render_template('login.html', title='Авторизация', form=form)
    else:
        return render_template('error_already_login.html', title='Уже зашел')


@app.route('/register', methods=['GET', 'POST'])
def register():
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
            if db_sess.query(Barber).filter(Barber.email == form.email.data).first():
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
def book():
    if current_user.is_authenticated:
        form = RecordForm()
        db_sess = db_session.create_session()
        categories = db_sess.query(Category).all()
        form.category.choices = [(c.id, c.name) for c in categories]
        if request.method == 'POST' and form.validate_on_submit():
            try:
                record = Record(
                    date_time=form.date_time.data,
                    user_id=current_user.id,
                )
                category = db_sess.query(Category).get(form.category.data)
                if category:
                    record.category.append(category)
                db_sess.add(record)
                db_sess.commit()
                flash('Запись успешно создана!', 'success')
                return redirect('/')
            except Exception as e:
                db_sess.rollback()
                print(e)
                flash('Произошла ошибка при создании записи', 'danger')

        return render_template('record_user.html', title='Запись', form=form, styles=categories)
    else:
        return render_template('error_book.html', title='Error')


@app.route('/usercard', methods=['GET'])
def usercard():
    if current_user.is_authenticated:
        db_sess = db_session.create_session()
        records = db_sess.query(Record).filter(Record.user_id == current_user.id).all()
        all_records = db_sess.query(Record).filter(Record.user_id == current_user.id).all()
        now = datetime.datetime.now()
        active_records = [r for r in all_records if r.date_time > now]
        inactive_records = [r for r in all_records if r.date_time <= now]
        return render_template('usercard.html',
                               user=current_user,
                               active_records=active_records,
                               inactive_records=inactive_records,
                               now=datetime.datetime.now())
    else:
        return render_template('no_reg_no_log_error.html', title='Error')


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
                if db_sess.query(User).filter(User.email == form.email.data).first():
                    return render_template('register_barber.html', title='Регистрация',
                                           form=form,
                                           message="Такой пользователь уже есть")
                if db_sess.query(Barber).filter(Barber.email == form.email.data).first():
                    return render_template('register_barber.html', title='Регистрация',
                                           form=form,
                                           message="Такой пользователь уже есть")

                filename = None
                if form.image.data:
                    file = form.image.data
                    filename = secure_filename(f"{form.surname.data}_{form.name.data}_{file.filename}")
                    file.save(os.path.join('static/images/barbers', filename))
                try:
                    barber = Barber(
                        email=form.email.data,
                        surname=form.surname.data,
                        name=form.name.data,
                        address=form.address.data,
                        city_from=form.city_from.data,
                        info=form.info.data,
                        image=filename,
                        is_barber=True
                    )
                    barber.set_password(form.password.data)
                    db_sess.add(barber)
                    db_sess.commit()
                    return redirect('/')
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
    return render_template('location.html')


@app.route('/barbers', methods=['GET', 'POST'])
def barbers():
    try:
        data = get(f'http://localhost:8080/api/barbers').json()
        barbers_list = data.get('barbers', [])
        return render_template('barbers.html', barbers=barbers_list)
    except Exception:
        return render_template('error_500.html', title='Error 500')


@app.route('/barber_card')
@login_required
def barber_card():
    if not current_user.is_barber:
        flash('Доступ запрещён', 'danger')
        return redirect(url_for('index'))
    db_sess = db_session.create_session()
    now = datetime.datetime.now()
    records = db_sess.query(Record).filter(
        Record.date_time > now
    ).all()

    return render_template('barber_card.html',
                           barber=current_user,
                           records=records)

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(400)
def bad_request(_):
    return make_response(jsonify({'error': 'Bad Request'}), 400)

if __name__ == '__main__':
    os.makedirs('static/images/barbers', exist_ok=True)
    os.makedirs('db', exist_ok=True)
    db_session.global_init("db/beatyweb.db")
    app.register_blueprint(barbers_api.blueprint)
    app.run(port=8080, host='127.0.0.1')