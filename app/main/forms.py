from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SubmitField
from wtforms.validators import Required, Length, Email
from wtforms import ValidationError
from ..api_1_0.models import Mail

class MailForm(FlaskForm):
    """The Mail form."""
    
    sender = StringField('sender', validators=[Required(), Email(), Length(max=Mail.MaxSenderLen)])
    recipient = StringField('recipient', validators=[Required(), Email(), Length(max=Mail.MaxRecipientLen)])
    subject = StringField('subject', validators=[Length(max=Mail.MaxSubjectLen)])
    content = TextAreaField('content', validators=[Length(max=Mail.MaxContentLen)])
    submit = SubmitField('send')
