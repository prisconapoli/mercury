from flask import Blueprint, url_for

api = Blueprint('api', __name__)
version = 'v1.0'

from . import mail, event, errors, exceptions,utils
from .decorators import json

def endpoints():
    """Get the main endpoints for the RESTful API """
    return {
        'Get email collection [GET]': url_for('api.get_mails'),
        'Create a new email [POST]': url_for('api.new_mail')
    }


@api.route('/')
@json
def index():
    """Provide the version and the main endpoint """

    return {'versions': {version: endpoints()}}