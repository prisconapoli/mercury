from flask import render_template, redirect
from .forms import MailForm
from . import main
from ..api_1_0.mail.views import *

import requests, json


def post_new_email(data):
    headers = {'Content-Type': 'application/json'}
    return requests.post(url_for('api.new_mail', _external=True), data=json.dumps(data), headers=headers)


@main.route('/', methods=['GET', 'POST'])
def index():
    form = MailForm()
    if form.validate_on_submit():
        data = {
            'sender': form.sender.data,
            'recipient': form.recipient.data,
            'subject': form.subject.data,
            'content': form.content.data
        }
        r = post_new_email(data)
        if r.ok and r.headers['Location']:
            return redirect(url_for('main.confirm', location=r.headers['Location']))
    return render_template('index.html', form=form)


@main.route('/confirm')
def confirm():
    if request.args.get('location'):
        return render_template('confirm.html', location=request.args.get('location'))
    return redirect(url_for('main.index'))
