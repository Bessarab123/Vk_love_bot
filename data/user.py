import sqlalchemy
from .db_session import SqlAlchemyBase
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'users'
    vk_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, primary_key=True)
    age = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    sex = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    city = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    scores = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    last_message = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    last_message_time = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True)
