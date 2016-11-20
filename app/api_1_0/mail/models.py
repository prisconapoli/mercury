from validate_email import validate_email
from flask import url_for
from ..utils import get_or_error
from ..mail_service.exceptions import ValidationError
from ... import db
from ..utils import post_event, build_event
from sqlalchemy import event


class Mail(db.Model):
    """The Mail model."""

    MaxSenderLen = 256
    MaxRecipientLen = 512
    MaxSubjectLen = 512
    MaxContentLen = 4096

    __tablename__ = 'mails'
    id = db.Column(db.Integer, primary_key=True)
    _sender = db.Column(db.String)
    _recipient = db.Column(db.String)
    _subject = db.Column(db.String, default='')
    _content = db.Column(db.Text, default='')
    _events = db.relationship('Event', backref='mail', lazy='dynamic')

    def sender(self):
        return self._sender

    def recipients(self):
        return self._recipient.split()

    def subject(self):
        return self._subject

    def content(self):
        return self._content

    def url(self):
        return url_for('api.get_mail', id=self.id, _external=True)

    def events(self):
        return self._events

    def to_dict(self):
        """ Return a Python dictionary representation of this object."""

        dict_mail = {
            'url': url_for('api.get_mail', id=self.id, _external=True),
            'sender': self._sender,
            'recipient': self._recipient,
            'subject': self._subject,
            'content': self._content,
            'events': url_for('api.get_events', id=self.id, _external=True),
        }
        return dict_mail

    def validate_email(self):
        """ Perform consistency check on mail fields

        Raises:
            ValidationError
        """

        sender = self._sender.split()
        if len(sender) > 1 or not validate_email(self._sender):
            raise ValidationError('Invalid sender address: %s' % self._sender)

        if len(self._sender) > Mail.MaxSenderLen:
            raise ValidationError('Maximum allowed size for sender is: %s' % Mail.MaxSenderLen)

        recipients = self._recipient.split()
        for recipient in recipients:
            if not validate_email(recipient):
                raise ValidationError('Invalid recipient address:%s' % recipient)

        if len(self._recipient) > Mail.MaxRecipientLen:
            raise ValidationError('Maximum allowed size for recipient is: %s' % Mail.MaxRecipientLen)

        if len(self._subject) and len(self._subject) > Mail.MaxSubjectLen:
            raise ValidationError('Maximum allowed size for subject is: %s' % Mail.MaxSubjectLen)

        if len(self._content) and len(self._content) > Mail.MaxContentLen:
            raise ValidationError('Maximum allowed size for content is: %s' % Mail.MaxContentLen)

    @staticmethod
    def from_dict(dict_mail):
        """ Create a new object from a dictionary. """

        sender = get_or_error(dict_mail, 'sender')
        recipient = get_or_error(dict_mail, 'recipient')
        subject = get_or_error(dict_mail, 'subject', nullable=True)
        content = get_or_error(dict_mail, 'content', nullable=True)
        return Mail(_sender=sender, _recipient=recipient, _subject=subject, _content=content)

