import flask
from . import db_session
from .barbers import Barber
from flask import jsonify, make_response, request

blueprint = flask.Blueprint(
    'barbers_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/barbers')
def get_barbers():
    db_sess = db_session.create_session()
    barbers = db_sess.query(Barber).all()
    return jsonify(
        {
            'barbers':
                [item.to_dict(only=('id', 'surname', 'name', 'image', 'info'))
                 for item in barbers]
        }
    )