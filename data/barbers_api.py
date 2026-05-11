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

@blueprint.route('/api/barbers/<int:barber_id>')
def get_barber(barber_id):
    db_sess = db_session.create_session()
    barber = db_sess.query(Barber).get(barber_id)
    return jsonify(
        {
            'barber':
                barber.to_dict(only=('id', 'surname', 'name', 'image', 'info'))
        }
    )