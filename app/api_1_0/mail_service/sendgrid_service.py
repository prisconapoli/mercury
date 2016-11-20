from sendgrid.helpers.mail import *
from .mail_service import *
from mail_config import MailConfig
import uuid
import sendgrid


class SendgridService(MailService):
    """ Send email using Sendgrid Service.

    This is a concrete class that inherits from MailService
    It requires the definition of these properties:
        SENDGRID_API_KEY

    All methods are thread safe. Required data are passed as arguments.
    Only local variable are used. There are no changes in the object status.
    """

    def __init__(self):
        self.id = str(uuid.uuid4())
        self.service_name = 'Sendgrid'
        self.sg = sendgrid.SendGridAPIClient(apikey=MailConfig.SENDGRID_API_KEY)

    def prepare_message(self, sender, subject, recipient, content):
        return Mail(Email(sender), subject,
                    Email(recipient), Content("text/plain", content))

    def send_message(self, message):
        return self.sg.client.mail.send.post(request_body=message.get())

    def response_details(self, response):
        return {'status_code': response.status_code,
                'body': response.body}
