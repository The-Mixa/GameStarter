import sqlalchemy
from .db_session import SqlAlchemyBase

from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from datetime import datetime

# id, id_пользователя, название игры, тип уведомления, дата создания
class Notification(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'notifications'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    for_user = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    game_name = sqlalchemy.Column(sqlalchemy.String, sqlalchemy.ForeignKey('games.name'))
    status_nice = sqlalchemy.Column(sqlalchemy.Boolean)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, 
                                     default=datetime.now)
    user = orm.relationship('User')
    game = orm.relationship('Game')

