from flask import Blueprint, url_for

api = Blueprint('api', __name__)
version = 'v1.0'

from . import mail, event, errors, exceptions,utils
from .decorators import json

def endpoints():
    """Get the main endpoint for the RESTful API """
    return {'mails_url': url_for('api.get_mails', _external=True)}


@api.route('/')
@json
def index():
    """Provide the version and the main endpoint """

    return {'versions': {version: endpoints()}}