import sqlalchemy
from .db_session import SqlAlchemyBase
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin


class User(SqlAlchemyBase):
    __tablename__ = 'users'
    vk_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=False, primary_key=True)
    age = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=16)
    sex = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    city = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    scores = sqlalchemy.Column(sqlalchemy.Integer, nullable=False, default=0)
    last_message = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    interlocutor = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    in_group = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False, default=True)
