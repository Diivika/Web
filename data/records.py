import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin


class Record(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'records'
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    date_time = sqlalchemy.Column(sqlalchemy.DateTime)
    user_id = sqlalchemy.Column(sqlalchemy.Integer)
    category = orm.relationship("Category",
                                  secondary="association",
                                  backref="records")
    barber_id = sqlalchemy.Column(sqlalchemy.Integer)
    is_finished = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    is_accepted = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    client_phone = sqlalchemy.Column(sqlalchemy.String)
    name = sqlalchemy.Column(sqlalchemy.String)
    surname = sqlalchemy.Column(sqlalchemy.String)
