from flask import url_for, current_app
from ..event.view import *
from .. import api
from ..decorators import json as jasonify
from ..decorators import collection
from ..utils import post_event, build_event
from ... import db
from ... import cache
from .models import Mail
from ..mail_service.exceptions import ValidationError
from ..mail_dispatcher.dispatcher import Dispatcher

name = 'Mail Service'


@api.route('/mails/', methods=['GET'])
@jasonify
@cache.cached(timeout=120)
@collection(Mail)
def get_mails():
    return Mail.query


@api.route('/mails/', methods=['POST'])
@jasonify
def new_mail():
    request_data = request.get_json(silent=True);

    if request_data is not None:
        mail = Mail.from_dict(request_data)
        db.session.add(mail)
        db.session.flush()
        db.session.commit()
        post_event('api.new_event',
                    mail.id, build_event(created_by=name, event='NEW', mail_id=mail.id))
        try:
           mail.validate_email()
        except ValidationError, e:
            post_event(
               'api.new_event', mail.id,
               build_event(created_by=name, event='BAD REQUEST', mail_id=mail.id))
            raise e

        post_event('api.new_event', mail.id, build_event(created_by=name, event='ACCEPTED', mail_id=mail.id))
        url_events = None if not current_app.config['TRACK_EVENTS'] else url_for('api.new_event',
                                                                                id=mail.id, _external=True)

        Dispatcher.dispatch(mail, url_events)
        return {}, 202, {'Location': mail.url()}
    else:
        abort(400)


@api.route('/mails/<int:id>', methods=['GET'])
@cache.cached(timeout=120)
@jasonify
def get_mail(id):
    return Mail.query.get_or_404(id)


