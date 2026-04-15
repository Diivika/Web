import sqlalchemy
from .db_session import SqlAlchemyBase
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import orm


class Record(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'records'
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    date_time = sqlalchemy.Column(sqlalchemy.DateTime,)
    category = orm.relationship("Category",
                                  secondary="association",
                                  backref="records")
