from flask import jsonify, request, abort, url_for,current_app

from .models import Mail,Event
from . import api
from .. import db
from .decorators import json,collection
from .utils import post_event,build_event
from .. import cache
from .dispatcher import Dispatcher

@api.route('/mails/', methods=['GET'])
@json
@cache.cached(timeout=120)
@collection(Mail)
def get_mails():
    return Mail.query

@api.route('/mails/', methods=['POST'])
@json
def new_mail():
    name = 'Mail Service'
    request_data = request.get_json(silent=True);

    if request_data is not None:
        mail = Mail.from_dict(request_data)
        db.session.add(mail)
        db.session.flush()
        db.session.commit()

        post_event('api.new_event', mail.id, build_event(created_by=name, \
            event='NEW', mail_id=mail.id))

        if mail.validate_email() == False:
            post_event('api.new_event', mail.id, build_event(name, 'BAD REQUEST', mail.id))
            abort(400)

        post_event('api.new_event', mail.id, build_event(created_by=name, \
            event='ACCEPTED', mail_id=mail.id))

        url_events = None if not current_app.config['TRACK_EVENTS'] else url_for('api.new_event', id=mail.id, _external=True) 
        Dispatcher.dispatch(mail, url_events)
        return {}, 202, {'Location': mail.get_url()}
    else:
        abort(400) 

@api.route('/mails/<int:id>', methods=['GET'])
@cache.cached(timeout=120)
@json
def get_mail(id):
    return Mail.query.get_or_404(id)


