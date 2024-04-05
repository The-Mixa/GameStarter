from flask import Flask, render_template
from data import db_session

from data.users import User
from data.games import Game

from datetime import datetime


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


def main():
    db_session.global_init("db/games.sqlite")
    session = db_session.create_session()
    app.run('127.0.0.1', port=800)

     
if __name__ == '__main__':
    main()
