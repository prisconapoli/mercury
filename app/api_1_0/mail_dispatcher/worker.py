from ..utils import post_event_url, build_event
from . import mail_services
from exceptions import Retry, MailServiceNotAvailable
from pybreaker import CircuitBreakerError
from ..mail_service.exceptions import *
import json


def process_message(caller, mail, service, attempts=[], url_events=None):
    """Background task to send an email with one of the mail providers

    Args:
        caller(str): the caller of this function, e.g. Dispatcher or Celery
        mail(Mail): a mail to send
        service(MailService): the service to use to send the email
        attempts(list of str): contains a list of the providers that
            failed to send the mail
        url_events(str): if present, the string will be used as url to store
        events about the sending process of the mail


    Raise: CircuitBreakerError
    """
    try:
        circuit_breaker = mail_services[service.name()][1]
        post_event_url(
            url_events,
            build_event(created_by=caller,
                        event='READY TO SEND',
                        mail_id=mail.id,
                        blob=json.dumps({'service': service.name()})))
        circuit_breaker.call(service.send, mail, url_events)
    except (CircuitBreakerError, MailServiceException, NetworkConnectionError) as ex:
        attempts.append(service.name())
        if len(attempts) < len(mail_services):
            post_event_url(
                url_events,
                build_event(
                    created_by=caller,
                    event='RETRY',
                    mail_id=mail.id,
                    blob=json.dumps({'service': service.name(), 'exception': str(ex)})))
            raise Retry('Retry')
        else:
            post_event_url(
                url_events,
                build_event(
                    created_by=caller,
                    event='DISCARDED',
                    mail_id=mail.id,
                    blob=json.dumps({'info': 'max numbers of attempts'})))
            raise MailServiceNotAvailable('No mail service available')
