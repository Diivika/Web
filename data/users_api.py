import flask
from . import db_session
from .users import User
from flask import jsonify, make_response, request

blueprint = flask.Blueprint(
    'users_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/users')
def get_users():
    db_sess = db_session.create_session()
    users = db_sess.query(User).all()
    return jsonify(
        {
            'users':
                [item.to_dict(only=('id', 'surname', 'name'))
                 for item in users]
        }
    )

@blueprint.route('/api/users/<int:user_id>')
def get_user(user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(user_id)
    return jsonify(
        {
            'user':
                user.to_dict(only=('id', 'surname', 'name'))
        }
    )