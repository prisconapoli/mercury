from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, Email
from ..api_1_0.mail.models import Mail


class MailForm(FlaskForm):
    """The Mail form."""
    
    sender = StringField('sender', validators=[DataRequired(), Email(), Length(max=Mail.MaxSenderLen)])
    recipient = StringField('recipient', validators=[DataRequired(), Email(), Length(max=Mail.MaxRecipientLen)])
    subject = StringField('subject', validators=[Length(max=Mail.MaxSubjectLen)])
    content = TextAreaField('content', validators=[Length(max=Mail.MaxContentLen)])
    submit = SubmitField('send')
