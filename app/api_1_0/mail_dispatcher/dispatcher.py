from flask import current_app
from queue import enqueue
from exceptions import Retry, MailServiceNotAvailable
from . import get_mail_service
from .worker import process_message
from ..utils import post_event_url, build_event


class Dispatcher(object):
    Name = "Dispatcher"

    @staticmethod
    def dispatch(mail, url_events=None):
        """Dispatch a mail message.

        If the application use a task queue, this method add a new task
        in the queue and returns immediately.
        Otherwise, the message will be processed.

        Args:
        mail(Mail): a mail to send

        url_events(str): if present, the string will be used as url to store
        events about the sending process of the mail

        """

        attempts = []
        if current_app.config['QUEUE'] is True:
            post_event_url(url_events, build_event(
                    created_by=Dispatcher.Name,
                    event='ENQUEUE', mail_id=mail.id))
            return enqueue.apply_async(args=[mail, attempts, url_events])
        else:
            service = get_mail_service(attempts)
            while service:
                try:
                    process_message(Dispatcher.Name, mail, service, attempts, url_events)
                    return
                except Retry:
                    service = get_mail_service(attempts)
                except MailServiceNotAvailable:
                    break

