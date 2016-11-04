from .. import db
from .utils import timestamp
from .exceptions import ValidationError
from flask import url_for
from validate_email import validate_email

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
        raise ValidationError('missing %s'%(key))
    return value if value is not None else ''

class Mail(db.Model):
    """The Mail model."""

    MaxSenderLen=256
    MaxRecipientLen=512
    MaxSubjectLen=512
    MaxContentLen=4096

    __tablename__ = 'mails'
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String)
    recipient = db.Column(db.String)
    subject = db.Column(db.String, default='')
    content = db.Column(db.Text, default='')
    events = db.relationship('Event', backref='mail', lazy='dynamic')

    def get_sender(self):
        return self.sender

    def get_recipient(self):
        return self.recipient.split()

    def get_subject(self):
        return self.subject

    def get_content(self):
        return self.content

    def get_url(self):
        return url_for('api.get_mail', id=self.id, _external=True)

    def to_dict(self):
        """ Return a Python dictionary representation of this object."""

        dict_mail = {
            'url': url_for('api.get_mail', id=self.id, _external=True),
            'sender' : self.sender,
            'recipient' : self.recipient,
            'subject' : self.subject,
            'content': self.content,
            'events': url_for('api.get_events', id=self.id, _external=True),
        }
        return dict_mail

    def validate_email(self):
        """ Perform consistency check on mail fields """

        sender = self.sender.split()
        if len(sender) > 1 or not validate_email(self.sender):
            raise ValidationError('Invalid sender address: %s'%self.sender)

        if len(self.sender) > Mail.MaxSenderLen:
            print ('Maximum allowed size for sender is: %s'%Mail.MaxSenderLen)
            raise ValidationError('Maximum allowed size for sender is: %s'%Mail.MaxSenderLen)

        recipients = self.recipient.split()
        for recipient in recipients:
            if not validate_email(recipient):
                raise ValidationError('Invalid recipient address:%s'%recipient)
        
        if len(self.recipient) > Mail.MaxRecipientLen:
            raise ValidationError('Maximum allowed size for recevier is: %s'%Mail.MaxRecipientLen)

        if len(self.subject) and  len(self.subject)> Mail.MaxSubjectLen:
            raise ValidationError('Maximum allowed size for subject is: %s'%Mail.MaxSubjectLen)

        if len(self.content) and len(self.content)> Mail.MaxContentLen:
            raise ValidationError('Maximum allowed size for content is: %s'%Mail.MaxContentLen)

    @staticmethod
    def from_dict(dict_mail):
        """ Create a new object from a dictionary. """
        
        sender=get_or_error(dict_mail, 'sender')
        recipient=get_or_error(dict_mail, 'recipient')
        subject=get_or_error(dict_mail, 'subject', nullable=True)
        content=get_or_error(dict_mail, 'content', nullable=True)
        return Mail(sender=sender, recipient=recipient, subject=subject, content=content);

class Event(db.Model):
    """The Event model."""

    __tablename__ = 'events'
    id=db.Column(db.Integer, primary_key=True)
    created_at=db.Column(db.BigInteger, default=timestamp)
    created_by=db.Column(db.String, default='')
    event=db.Column(db.String)
    mail_id=db.Column(db.Integer, db.ForeignKey('mails.id'))
    blob=db.Column(db.String, default='')

    def get_url(self):
        return url_for('api.get_event', mail_id=self.mail_id, event_id=self.id, _external=True)

    def to_dict(self):
        """ Return a Python dictionary representation of this object."""

        dict_event = {
            'created_at': self.created_at,
            'created_by': self.created_by,
            'event': self.event,
            'mail_id' : self.mail_id,
            'blob':self.blob
        }

        return dict_event

    @staticmethod
    def from_dict(dict_event, nullable=False):
        """ Create a new object from a dictionary. """

        event=Event()
        event.created_at=get_or_error(dict_event, 'created_at', nullable=True)
        event.created_by=get_or_error(dict_event, 'created_by', nullable=True)
        event.event=get_or_error(dict_event, 'event')
        event.mail_id=get_or_error(dict_event, 'mail_id', nullable=True)
        event.blob=get_or_error(dict_event, 'blob', nullable=True)        
        return event;