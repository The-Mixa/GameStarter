from flask import Blueprint, jsonify, make_response, request

from . import db_session
from .users import User

blueprint = Blueprint(
    'users_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/users')
def get_users():
    db_sess = db_session.create_session()
    users = db_sess.query(User).all()
    s = []
    for item in users:
        user = item.to_dict(only=('id', 'name', 'nickname', 'is_moderator', 'email'))
        user['games'] = [{'id': game.id, 'name': game.name} for game in item.games]
        s += [user]

    return jsonify(
        {
            'users': s

        }
    )


@blueprint.route('/api/users/<int:user_id>', methods=['GET'])
def get_one_user(user_id):
    db_sess = db_session.create_session()
    item = db_sess.query(User).get(user_id)
    if not item:
        return make_response(jsonify({'error': 'Not found'}), 404)
    user = item.to_dict(only=('id', 'name', 'nickname', 'is_moderator', 'email'))
    user['games'] = [{'id': game.id, 'name': game.name} for game in item.games]
    return jsonify(
        {'user': user}
    )
