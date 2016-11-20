from flask import request, abort
from .models import Event
from ..mail.models import Mail
from .. import api
from ..decorators import json, collection
from ... import db
from ... import cache


@api.route('/mails/<int:id>/events/')
@json
@cache.cached(timeout=10)
@collection(Event)
def get_events(id):
    mail = Mail.query.get_or_404(id)
    return mail.events()


@api.route('/mails/<int:id>/events/', methods=['POST'])
@json
def new_event(id):
    request_data = request.get_json(silent=True)
    if request_data is not None:
        Mail.query.get_or_404(id)
        event = Event.from_dict(request_data)
        db.session.add(event)
        db.session.flush()
        db.session.commit()
        return {}, 201, {'Location': event.url()}
    else:
        abort(400)


@api.route('/mails/<int:mail_id>/events/<int:event_id>')
@json
@cache.cached(timeout=120)
def get_event(mail_id, event_id):
    event = Event.query.get_or_404(event_id)
    if event.mail_id() == mail_id:
        return event
    abort(404)
