from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, Email
from app.api_1_0.mail.models import Mail


class MailForm(FlaskForm):
    """A form for an email."""
    sender = StringField('Sender', validators=[DataRequired(), Email(), Length(max=Mail.MaxSenderLen)])
    recipients = StringField('Recipients', validators=[DataRequired(), Email(), Length(max=Mail.MaxRecipientLen)])
    subject = StringField('Subject', validators=[Length(max=Mail.MaxSubjectLen)])
    content = TextAreaField('Content', validators=[Length(max=Mail.MaxContentLen)])


class SendMailForm(MailForm):
    """A form to send an email."""
    submit = SubmitField('Send')


class EventForm(FlaskForm):
    """A form for an event."""
    id = StringField('Id')
    created_at = StringField('Created at')
    created_by = StringField('Created by')
    event = StringField('Event')
    mail_id = StringField('Mail Id')
    blob = TextAreaField('Blob')

