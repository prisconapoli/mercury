from flask import jsonify, render_template
from .exceptions import ValidationError
from . import api

def bad_request(message):
    response = jsonify({'error': 'bad request', 'message': message})
    response.status_code = 400
    return response

@api.errorhandler(ValidationError)
def validation_error(e):
    return bad_request(e.args[0])


@api.app_errorhandler(404)
def page_not_found(e):
    response = jsonify({'error': 'Not Found'})
    response.status_code = 404
    return response

@api.app_errorhandler(400)
def internal_server_error(e):
    response = jsonify({'error': 'Bad Request'})
    response.status_code = 404
    return response

@api.app_errorhandler(500)
def internal_server_error(e):
    response = jsonify({'error': 'Internal Server Error'})
    response.status_code = 500
    return response
