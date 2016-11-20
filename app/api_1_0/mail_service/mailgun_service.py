from .mail_service import *
from mail_config import MailConfig
import uuid
import requests


class MailgunService(MailService):
    """ Send email using Mailgun Service.

    This is a concrete class that inherits from MailService
    It requires the definition of these properties:
        MAILGUN_URL_API
        MAILGUN_DOMAIN_NAME
        MAILGUN_API_KEY

    All methods are thread safe. Required data are passed as arguments.
    No changes in the object status after it has been created.
    """

    def __init__(self):
        self.id = str(uuid.uuid4())
        self.service_name = 'Mailgun'
        self.url = MailConfig.MAILGUN_URL_API.format(MailConfig.MAILGUN_DOMAIN_NAME)
        self.auth = ('api', MailConfig.MAILGUN_API_KEY)

    def prepare_message(self, sender, subject, recipient, content):
        return {
            'from': sender,
            'to': recipient,
            'subject': subject,
            'text': content,
        }

    def send_message(self, message):
        return requests.post(url=self.url, auth=self.auth, data=message, timeout=1)

    def response_details(self, response):
        return {
                'status_code': response.status_code,
                'reason': response.reason,
                'text': response.text}

