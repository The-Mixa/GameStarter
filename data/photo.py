import sqlalchemy
from .db_session import SqlAlchemyBase

from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin


# id, путь до файла, id игры
class Photo(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'photo'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    path = sqlalchemy.Column(sqlalchemy.String)
    parent_game = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("games.id"))
    game = orm.relationship('Game')

