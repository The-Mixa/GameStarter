import sqlalchemy
from .db_session import SqlAlchemyBase

from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin


association_table = sqlalchemy.Table(
    'association',
    SqlAlchemyBase.metadata,
    sqlalchemy.Column('game_when_collaborate', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('users.id')),
    sqlalchemy.Column('collaborator', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('games.id'))
)

class Game(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'games'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    author = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    collaborators = orm.relationship('User', backref='game_when_collaborate', secondary="association")                     
    is_finished = sqlalchemy.Column(sqlalchemy.Boolean, default=True)
    user = orm.relationship('User')