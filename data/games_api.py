from flask import Blueprint, jsonify, make_response, request

from . import db_session
from .games import Game

blueprint = Blueprint(
    'games_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/games')
def get_jobs():
    db_sess = db_session.create_session()
    game = db_sess.query(Game).all()
    return jsonify(
        {
            'games':
                [item.to_dict(
                    only=('id', 'author', 'name', 'description',
                          'github_link')
                ) for item in game]
        }
    )


@blueprint.route('/api/games/<int:game_id>', methods=['GET'])
def get_one_job(game_id):
    db_sess = db_session.create_session()
    game = db_sess.query(Game).get(game_id)
    if not game:
        return make_response(jsonify({'error': 'Not found'}), 404)
    return jsonify(
        {'game': game.to_dict(only=('id', 'author', 'name', 'description',
                                    'github_link'))}
    )
