from app import queue
from ..utils import post_event_url, build_event
from .worker import process_message
from . import get_mail_service
from exceptions import Retry, MailServiceNotAvailable
from ..mail_service.exceptions import *

name = "Celery"


@queue.task(bind=True, default_retry_delay=5)
def enqueue(self, mail, attempts=[], url_events=None):
    """Background task to send an email with one of the mail providers

    Args:
        self(Celery)
        mail(Mail): a mail to send
        attempts(list of str): contains a list of the providers that
            failed to send the mail
        url_events(str): if present, the string will be used as url to store
        events about the sending process of the mail

    Raise: MailServiceNotAvailable

    """
    post_event_url(
        url_events,
        build_event(created_by=name, event='DEQUEUE', mail_id=mail.id))
    service = get_mail_service(attempts)
    try:
        process_message(name, mail, service, attempts, url_events)
    except Retry as ex:
        raise self.retry(exc=ex)
    except MailServiceNotAvailable:
        pass

