import sqlalchemy
from .db_session import SqlAlchemyBase
from werkzeug.security import generate_password_hash, check_password_hash

from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin


class Comment(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'comments'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    userid = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    gameid = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("games.id"))
    text = sqlalchemy.Column(sqlalchemy.Text)
    likes = sqlalchemy.Column(sqlalchemy.Integer)
    dislikes = sqlalchemy.Column(sqlalchemy.Integer)

    user = orm.relationship('User')
    game = orm.relationship('Game')
