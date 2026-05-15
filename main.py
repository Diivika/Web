import datetime
import os
from flask import Flask, url_for, request, render_template, redirect, abort, jsonify, flash
from flask import make_response
from requests import get
from flask_login import LoginManager, login_user
from flask_login import login_required, logout_user, current_user
from flask_restful import Api
from werkzeug.utils import secure_filename

from bot.main import notify_user_about_booking
from data import db_session, barbers_api
from data.users import User
from data.records import Record
from data.category import Category
from data.barbers import Barber
from forms.login_user_form import LoginForm
from forms.record_user_form import RecordForm
from forms.register_barber_form import RegisterBarberForm
from forms.register_user_form import RegisterUserForm
import shutil
from datetime import time

os.makedirs('db', exist_ok=True)
db_session.global_init(os.path.join(os.path.dirname(__file__), 'db', 'beatyweb.db'))
db_sess = db_session.create_session()
app = Flask(__name__, template_folder='static/templates')
api = Api(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(compound_id):
    db_sess = db_session.create_session()
    if compound_id.startswith('barber_'):
        real_id = int(compound_id.replace('barber_', ''))
        return db_sess.query(Barber).get(real_id)
    elif compound_id.startswith('user_'):
        real_id = int(compound_id.replace('user_', ''))
        return db_sess.query(User).get(real_id)
    return None


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
                if hasattr(user, 'is_barber') and user.is_barber:
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
        barbers = db_sess.query(Barber).filter(Barber.is_barber == True).all()
        form.barber.choices = [(b.id, f'{b.name} {b.surname}') for b in barbers]
        if request.method == 'POST' and form.validate_on_submit():
            try:
                date_time = form.date_time.data
                weekday = date_time.weekday()
                hour = date_time.hour
                minute = date_time.minute
                if date_time <= datetime.datetime.now():
                    flash('Нельзя записаться на прошедшее время', 'danger')
                    return render_template('record_user.html', title='Запись', form=form, styles=categories,
                                           barbers=barbers)
                if minute != 0:
                    flash('Запись возможна только в начале часа (например, 10:00, 11:00, 12:00)', 'danger')
                    return render_template('record_user.html', title='Запись', form=form, styles=categories,
                                           barbers=barbers)
                if weekday <= 4:
                    if hour < 10 or (hour == 21 and minute > 0) or hour >= 21:
                        flash('ПН-ПТ мы работаем с 10:00 до 21:00', 'danger')
                        return render_template('record_user.html', title='Запись', form=form, styles=categories,
                                               barbers=barbers)
                else:
                    if hour < 11 or (hour == 20 and minute > 0) or hour >= 20:
                        flash('СБ-ВС мы работаем с 11:00 до 20:00', 'danger')
                        return render_template('record_user.html', title='Запись', form=form, styles=categories,
                                               barbers=barbers)
                existing = db_sess.query(Record).filter(
                    Record.barber_id == form.barber.data,
                    Record.date_time == date_time,
                    Record.is_accepted != False
                ).first()
                if existing:
                    flash('Это время уже занято, выберите другое', 'danger')
                    return render_template('record_user.html', title='Запись', form=form, styles=categories,
                                           barbers=barbers)
                record = Record(
                    date_time=date_time,
                    user_id=current_user.id,
                    barber_id=form.barber.data,
                    client_phone=form.client_phone.data,
                    name=current_user.name,
                    surname=current_user.surname
                )
                category = db_sess.get(Category, form.category.data)
                if category:
                    record.category.append(category)
                db_sess.add(record)
                db_sess.commit()
                notify_user_about_booking(current_user.id)
                flash('Запись успешно создана!', 'success')
                return redirect('/usercard')

            except Exception as e:
                db_sess.rollback()
                print(e)
                flash('Произошла ошибка при создании записи', 'danger')

        return render_template('record_user.html', title='Запись', form=form, styles=categories, barbers=barbers)
    else:
        return render_template('error_book.html', title='Error')


@app.route('/usercard', methods=['GET'])
def usercard():
    if current_user.is_authenticated:
        db_sess = db_session.create_session()
        records = db_sess.query(Record).filter(Record.user_id == current_user.id).all()
        all_records = db_sess.query(Record).filter(Record.user_id == current_user.id).all()
        now = datetime.datetime.now()
        active_records = [r for r in all_records if r.date_time > now and not r.is_finished]
        inactive_records = [r for r in all_records if r.date_time <= now or r.is_finished]
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
        if current_user.is_admin:
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
                    os.makedirs(os.path.join('static/images', 'barbers_portfolio'), exist_ok=True)
                    os.makedirs(os.path.join('static/images/barbers_portfolio', str(barber.id)), exist_ok=True)
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
        return render_template('error_403.html', title='Error 403')
    db_sess = db_session.create_session()
    now = datetime.datetime.now()
    records = db_sess.query(Record).filter(
        Record.barber_id == current_user.id,
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


@app.route('/barber_portfolio/<int:id>', methods=['GET', 'POST'])
def portfolio(id):
    db_sess = db_session.create_session()
    barber = db_sess.query(Barber).get(id)
    portfolio_path = os.path.join('static/images/barbers_portfolio', str(id))
    if os.path.exists(portfolio_path):
        photos = os.listdir(portfolio_path)
        photos = [f for f in photos if f.endswith(('.jpg', '.png', '.jpeg', '.gif'))]
    return render_template('portfolio.html', photos=photos, barber=barber)


@app.route('/add_photo/<int:barber_id>', methods=['POST'])
@login_required
def add_photo(barber_id):
    if current_user.id != barber_id and not current_user.is_admin:
        return render_template('error_403.html', title='Error 403')
    if 'photo' not in request.files:
        return redirect(url_for('portfolio', id=barber_id))
    file = request.files['photo']
    if file.filename == '':
        return redirect(url_for('portfolio', id=barber_id))
    if file:
        filename = secure_filename(f"{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}")
        portfolio_path = os.path.join('static/images/barbers_portfolio', str(barber_id))
        os.makedirs(portfolio_path, exist_ok=True)
        file.save(os.path.join(portfolio_path, filename))
    return redirect(url_for('portfolio', id=barber_id))


@app.route('/delete_photo/<int:barber_id>/<path:photo_name>', methods=['POST'])
@login_required
def delete_photo(barber_id, photo_name):
    if current_user.id != barber_id and not current_user.is_admin:
        return render_template('error_403.html', title='Error 403')
    photo_path = os.path.join('static/images/barbers_portfolio', str(barber_id), photo_name)
    if os.path.exists(photo_path):
        os.remove(photo_path)
        return jsonify({'success': True})
    return jsonify({'success': False})


@app.route('/delete_barber/<int:barber_id>', methods=['POST'])
@login_required
def delete_barber(barber_id):
    if not current_user.is_admin:
        return render_template('error_403.html', title='Error 403')
    db_sess = db_session.create_session()
    barber = db_sess.query(Barber).get(barber_id)
    try:
        if barber.image:
            image_path = os.path.join('static/images/barbers', barber.image)
            if os.path.exists(image_path):
                os.remove(image_path)
        portfolio_path = os.path.join('static/images/barbers_portfolio', str(barber_id))
        if os.path.exists(portfolio_path):
            shutil.rmtree(portfolio_path)
        db_sess.delete(barber)
        db_sess.commit()
        return jsonify({'success': True})
    except Exception as e:
        print(e)
        return render_template('error_500.html', title='Error 500')


@app.route('/accept_record/<int:record_id>', methods=['POST'])
@login_required
def accept_record(record_id):
    if not current_user.is_barber:
        return jsonify({'success': False, 'error': 'Доступ запрещён'})
    db_sess = db_session.create_session()
    record = db_sess.query(Record).get(record_id)
    if record and record.barber_id == current_user.id:
        record.is_accepted = True
        db_sess.commit()
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Запись не найдена'})


@app.route('/reject_record/<int:record_id>', methods=['POST'])
@login_required
def dreject_record(record_id):
    if not current_user.is_barber:
        return jsonify({'success': False, 'error': 'Доступ запрещён'})
    db_sess = db_session.create_session()
    record = db_sess.query(Record).get(record_id)
    if record and record.barber_id == current_user.id:
        db_sess.delete(record)
        db_sess.commit()
        return jsonify({'success': True})

@app.route('/finish_record/<int:record_id>', methods=['POST'])
@login_required
def finish_record(record_id):
    if not current_user.is_barber:
        return jsonify({'success': False, 'error': 'Доступ запрещён'})
    db_sess = db_session.create_session()
    record = db_sess.query(Record).get(record_id)
    if record and record.barber_id == current_user.id:
        record.is_finished = True
        db_sess.commit()
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Запись не найдена'})


if __name__ == '__main__':
    os.makedirs('static/images/barbers', exist_ok=True)
    db_session.global_init(os.path.join(os.path.dirname(__file__), 'db', 'beatyweb.db'))
    app.register_blueprint(barbers_api.blueprint)
    app.run(port=8080, host='127.0.0.1')
