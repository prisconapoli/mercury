from flask import render_template, redirect
from .forms import SendMailForm, MailForm, EventForm
from . import main
from ..api_1_0.mail.views import *
from .. import cache

import json
import requests


headers = {'Content-Type': 'application/json'}


def post_new_email(data):
    return requests.post(url_for('api.new_mail', _external=True), data=json.dumps(data), headers=headers)


@main.route('/', methods=['GET', 'POST'])
def index():
    form = SendMailForm()
    if form.validate_on_submit():
        data = {
            'sender': form.sender.data,
            'recipients': form.recipients.data,
            'subject': form.subject.data,
            'content': form.content.data
        }
        r = post_new_email(data)
        if r.ok and r.headers['Location']:
            return redirect(url_for('main.confirm', location=r.headers['Location'], mail_id=r.headers['MailId']))
    return render_template('index.html', form=form)


@main.route('/confirm')
def confirm():
    if request.args.get('location'):
        return render_template('confirm.html', location=request.args.get('location'),
                               mail_id=request.args.get('mail_id'))
    return redirect(url_for('main.index'))


@main.route('/details/mails/<int:id>', methods=['GET'])
@cache.memoize(timeout=60)
def mail_details(id):
    response = requests.get(url_for('api.get_mail', id=id, _external=True), headers=headers)
    if response.ok:
        mail = Mail.from_dict(json.loads(response.content))
        form = MailForm()
        form.content.data = mail.content()
        form.sender.data = mail.sender()
        form.subject.data = mail.subject()
        form.recipients.data = ' '.join(map(str, mail.recipients()))
        return render_template('mail_details.html', form=form)
    return abort(404)


@main.route('/details/mails/<int:id>/events/', methods=['GET'])
@cache.memoize(timeout=10)
def events_details(id):
    response = requests.get(url_for('api.get_events', id=id, _external=True), headers=headers)
    if response.ok:
        events = json.loads(response.content)
        return render_template('events_details.html', events=events["events"])
    return abort(404)


@main.route('/details/mails/<int:mail_id>/events/<int:event_id>', methods=['GET'])
@cache.memoize(timeout=60)
def event_detail(mail_id, event_id):
    response = requests.get(url_for('api.get_event', mail_id=mail_id, event_id=event_id, _external=True),
                            headers=headers)
    if response.ok:
        event = json.loads(response.content)
        form = EventForm()
        form.id.data = event["id"]
        form.created_at.data = event["created_at"]
        form.created_by.data = event["created_by"]
        form.event.data = event["event"]
        form.mail_id.data = event["mail_id"]
        form.blob.data = event["blob"]
        return render_template('event_details.html', form=form)
    return abort(404)
