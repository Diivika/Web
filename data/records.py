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
