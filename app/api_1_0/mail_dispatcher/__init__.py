from ..mail_service.exceptions import ValidationError
from ..mail_service.mailgun_service import MailgunService
from ..mail_service.sendgrid_service import SendgridService
import pybreaker
import random

mailgun = MailgunService()
sendgrid = SendgridService()
cb_mailgun = pybreaker.CircuitBreaker(fail_max=5, reset_timeout=60, exclude=[ValidationError])
cb_sendgrind = pybreaker.CircuitBreaker(fail_max=5, reset_timeout=60, exclude=[ValidationError])

service_registry = {
    mailgun.name(): (mailgun, cb_mailgun),
    sendgrid.name(): (sendgrid, cb_sendgrind)
}


def get_mail_service(attempts):
    """Select a mail service provider in healthy status to send an email.

    For a new request, the provider is chosen randomly.
    Otherwise, this function return a provider
    that has never been selected before.

    Args:
        attempts (list of str): contains the name of
        the providers already chosen to process this request

    Returns:
        MailService: a mail service object, otherwise None
    """

    available_services = [service for service in service_registry.keys() if service not in attempts]
    if len(available_services) is 0:
        return None

    i = random.randrange(0, 100) % len(available_services)
    return service_registry[available_services[i]][0]
