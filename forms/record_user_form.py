from flask_wtf import FlaskForm
from wtforms.fields.choices import SelectField
from wtforms.fields.datetime import DateField
from wtforms.fields.simple import SubmitField
from wtforms.validators import DataRequired


class RecordForm(FlaskForm):
    date = DateField('Дата стрижки', validators=[DataRequired()])
    submit = SubmitField('Записаться')