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
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    github_link = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    in_moderate = sqlalchemy.Column(sqlalchemy.Boolean, nullable=True)
    game_files = sqlalchemy.Column(sqlalchemy.String, nullable=True)                  
    likes = sqlalchemy.Column(sqlalchemy.Integer)
    dislikes = sqlalchemy.Column(sqlalchemy.Integer)
    photo = orm.relationship('Photo', back_populates='game')


    
    user = orm.relationship('User')
    comments = orm.relationship('Comment', back_populates='game')
