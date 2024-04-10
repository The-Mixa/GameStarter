import sqlalchemy
from .db_session import SqlAlchemyBase
from werkzeug.security import generate_password_hash, check_password_hash

from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin


class User(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    nickname = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    role = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    favorites = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    email = sqlalchemy.Column(sqlalchemy.String, nullable=True, unique=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    games_when_collaborate = orm.relationship('Game', backref='collaborator', secondary="association")
    
    games = orm.relationship("Game", back_populates='user')
    comments = orm.relationship('Comment', back_populates='user')

    games_likes = orm.relationship('Game', back_populates='user')
    games_dislikes = orm.relationship('Game', back_populates='user')
    comment_likes = orm.relationship('Comment', back_populates='user')
    comment_dislikes = orm.relationship('Comment', back_populates='user')

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)