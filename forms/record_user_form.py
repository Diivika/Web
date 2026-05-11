from flask_wtf import FlaskForm
from wtforms.fields.choices import SelectField
from wtforms.fields.datetime import DateField, DateTimeField
from wtforms.fields.simple import SubmitField, StringField
from wtforms.validators import DataRequired, Length


class RecordForm(FlaskForm):
    date_time = DateTimeField('Дата стрижки', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    submit = SubmitField('Записаться')
    category = SelectField('Услуга', choices=[], coerce=int, validators=[DataRequired()])
    barber = SelectField('Барбер', choices=[], coerce=int, validators=[DataRequired()])
    client_phone = StringField('Телефон', validators=[DataRequired(), Length(min=10, max=15)])