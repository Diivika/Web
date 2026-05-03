from flask_wtf import FlaskForm
from wtforms.fields.choices import SelectField
from wtforms.fields.datetime import DateField, DateTimeField
from wtforms.fields.simple import SubmitField
from wtforms.validators import DataRequired


class RecordForm(FlaskForm):
    date_time = DateTimeField('Дата стрижки', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    submit = SubmitField('Записаться')
    category = SelectField('Услуга', choices=[], coerce=int, validators=[DataRequired()])
