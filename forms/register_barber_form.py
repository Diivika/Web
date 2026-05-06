from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import PasswordField, StringField, SubmitField, EmailField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length


class RegisterBarberForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password_again = PasswordField('Repeat password', validators=[DataRequired()])
    surname = StringField('Surname', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired()])
    city_from = StringField('City', validators=[DataRequired()])
    info = TextAreaField('Информация о барбере', validators=[Length(max=500)])
    image = FileField('Фото барбера', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Только изображения!')])
    submit = SubmitField('Register')