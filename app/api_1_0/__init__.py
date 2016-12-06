from flask import Blueprint, url_for
api = Blueprint('api', __name__)
version = 'v1.0'

from . import mail, event, errors, utils
from .decorators import json


def endpoints():
    """Get the main endpoints for the RESTful API """
    return {
        'Retrieve the collection of all the email [GET]': url_for('api.get_mails', external=True),
        'Create a new email [POST]': url_for('api.new_mail', external=True)
    }


@api.route('/')
@json
def index():
    """Provide the version and the main endpoint """

    return {'versions': {version: endpoints()}}
