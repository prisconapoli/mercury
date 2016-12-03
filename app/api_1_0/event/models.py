from ... import db
from flask import url_for
from ..utils import timestamp, get_or_error


class Event(db.Model):
    """The Event model."""

    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    _created_at = db.Column(db.BigInteger, default=timestamp)
    _created_by = db.Column(db.String, default='')
    _event = db.Column(db.String)
    _mail_id = db.Column(db.Integer, db.ForeignKey('mails.id'))
    _blob = db.Column(db.String, default='')

    def url(self):
        return url_for('api.get_event', mail_id=self._mail_id, event_id=self.id, _external=True)

    def mail_id(self):
        return self._mail_id

    def to_dict(self):
        """ Return a Python dictionary representation of this object."""

        dict_event = {
            'id': self.id,
            'created_at': self._created_at,
            'created_by': self._created_by,
            'event': self._event,
            'mail_id': self._mail_id,
            'blob': self._blob
        }

        return dict_event

    @staticmethod
    def from_dict(dict_event):
        """ Create a new object from a dictionary. """

        event = Event()
        event._created_at = get_or_error(dict_event, 'created_at', nullable=True)
        event._created_by = get_or_error(dict_event, 'created_by', nullable=True)
        event._event = get_or_error(dict_event, 'event')
        event._mail_id = get_or_error(dict_event, 'mail_id', nullable=True)
        event._blob = get_or_error(dict_event, 'blob', nullable=True)
        return event
