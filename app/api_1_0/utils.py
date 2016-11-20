import time
import json
import requests
from flask import url_for, abort,current_app
from .mail_service.exceptions import ValidationError


def timestamp():
    """Get the current system time from epoch in nanosecond
    Returns:
        long:current system time
    """

    return long(time.time()*1e9)


def post_event(url, id, data):
    """Post an event for a mail.

    The event will be sent if TRACK_EVENTS is True, otherwise 
    the function returns silently
    
    Args:
        url(str): the endpoint defined as route, e.g. 'api.new_event'
        id(int): mail identifier
        data(dict): additional data to attach for this event
    """

    if current_app.config['TRACK_EVENTS']:
        return post_event_url(url_for(url, id=id, _external=True), data)


def post_event_url(url=None, data=None):
    """Post an event to a specific url.

    The event will be sent if the parameter ''url is not None.
    Args:
        url(str): complete url, e.g. http://<server>/api/v1.0/mails/<id>/events
        data(dict): additional data to attach for the event
    """
    if url is None:
        return
    headers = {'Content-Type': 'application/json'}
    r = requests.post(url, data=json.dumps(data) if data else '', headers=headers)
    if not r.ok:
        print "r.status_code", r.status_code
        abort(500)
    return r


def build_event(created_by, event, mail_id, created_at=None, blob=''):
    """ Utility function to create a generic event

    Args:
        created_by(str): creator of the event 
        event(str): event name
        mail_id(int): reference to mail id
        created_at(str): the creation time of this event. Default is None
        blob(str): data to attach. Defaults is is an empty string

    Returns:
        dict: a dictionary as below
        value = {
            'created_at': created_at,
            'created_by': created_by,
            'event': event,
            'mail_id' : mail_id,
            'blob':blob
        }
    """
    return {
        'created_at': created_at if created_at else timestamp(),
        'created_by': created_by,
        'event': event,
        'mail_id': mail_id,
        'blob': blob
    }


def get_or_error(dict_event, key, nullable=False):
    """Check if value is present in the dictionary

    Args:
        dict_event(dict): input dictionary
        key(str): key to search
        nullable(bool): true id the value is not compulsory. Defaults is false

    Raise:
        ValidationError if the value is compulsory

    """

    value = dict_event.get(key)
    if (value is None or value == '') and nullable is False:
        raise ValidationError('missing %s' % key)
    return value if value is not None else ''
