from .. import queue
from .mail_service import mail_services
from utils import timestamp, post_event_url,build_event
from .mail_service.mail_service import MailServiceException
import json
import random
from flask import current_app

def get_mail_provider(attempts):
    """Pick a mail providers to send the email.

    For a new request, the providers is choosen randomly.
    Otherwise, this function return a provider that has
    never been selected before

    Args:
    attempts (list of str): contains the name of
    the providers already choosen to process this request
    """

    if len(attempts):
        for server in mail_services.keys():
            if server not in attempts:
                return (server, mail_services[server])
    else:
        i = random.randrange(0, 1e9)%len(mail_services)
        return (mail_services.keys()[i], mail_services.values()[i])

class Dispatcher(object):
    Name = 'DISPATCHER'
    @staticmethod
    def dispatch(mail, url_events=None):
        """Dispatch a mail to a mail providers

        Args:
        url_events(str): if present, the string represents an url that can be used
        to log events about this mail
        """

        attempts = []
        if current_app.config['QUEUE'] is True:
            post_event_url(url_events, build_event(created_by=Dispatcher.Name, \
                event=('ENQUEUE'), mail_id=mail.id))
            return enqueue.apply_async(args=[mail, attempts, url_events])
        else:
            (service_name, service) = get_mail_provider(attempts)
            while service_name is not None:
                attempts.append(service_name)
                try:
                    post_event_url(url_events, build_event(created_by=Dispatcher.Name, \
                        event=('READY TO SEND'), mail_id=mail.id, blob=json.dumps({'service':service_name})))
                    service.send(mail, url_events)
                    return True
                except Exception as ex:
                    post_event_url(url_events, build_event(created_by=Dispatcher.Name, \
                        event=('RETRY'), mail_id=mail.id, blob=json.dumps({'service':service_name, 'exception':str(ex)})))
                    (service_name, service) = get_mail_provider(attempts)
            post_event_url(url_events, build_event(created_by=Dispatcher.Name, \
                    event=('DISCARDED'), mail_id=mail.id, blob=json.dumps({'info':'max numbers of attempts'}))) 


@queue.task(bind=True, default_retry_delay=5)
def enqueue(self, mail, attempts=[], url_events=None):
    """Background task to send an email with one of the mail providers"""
    
    name = 'CELERY_QUEUE'
    post_event_url(url_events, build_event(created_by=name, \
            event=('ENQUEUED'), mail_id=mail.id))
    
    (service_name, service)= get_mail_provider(attempts)
    
    if service is not None:
        attempts.append(service_name)
        try:
            post_event_url(url_events, build_event(created_by=name, \
                event=('READY TO SEND'), mail_id=mail.id, blob=json.dumps({'service':service_name})))
            service.send(mail, url_events)
        except Exception as ex:
            post_event_url(url_events, build_event(created_by=name, \
                event=('RETRY'), mail_id=mail.id, blob=json.dumps({'service':service_name, 'exception':str(ex)})))
            raise self.retry(exc=ex)

    else:
        post_event_url(url_events, build_event(created_by=name, \
            event=('DISCARDED'), mail_id=mail.id, blob=json.dumps({'info':'max numbers of attempts'}))) 

