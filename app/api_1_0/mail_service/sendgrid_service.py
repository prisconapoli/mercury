from sendgrid.helpers.mail import *
from ..utils import post_event_url,build_event
from .mail_service import *
from mail_config import MailConfig
import uuid
import json
import requests
import sendgrid

class SendgridService(MailService):
    """ Send email using Sendgrid Service.

    This is a concrete class that inherits from MailService
    It requires the definition of these properties:
        SENDGRID_API_KEY
    """

    Name = 'Sendgrid'
    def __init__(self):
        self.id = str(uuid.uuid4())
        self.sg = sendgrid.SendGridAPIClient(apikey=MailConfig.SENDGRID_API_KEY)

    def info(self, key):
        pass

    def name(self):
        return SendgridService.Name + ":" + self.id 

    def send(self, mail, url_events=None):
        #The sendgrid mail helper does not support multiple recipients
        #Send one mail per time
        try:
            for recipient in mail.get_recipient():
                sendgrind_mail = Mail(
                    Email(mail.get_sender()), mail.get_subject(),
                    Email(recipient), Content("text/plain", mail.get_content()))

                post_event_url(
                    url_events,
                    build_event(
                        created_by=self.name(),
                        event='SEND',
                        mail_id=mail.id,
                        blob=json.dumps({'to': recipient})))

                response = self.sg.client.mail.send.post(request_body=sendgrind_mail.get())
                self.postprocess(resp=response, mail=mail, url_events=url_events)
            return True
        except requests.exceptions.RequestException as e:
            raise MailServiceException(*e.args)
        except Exception as e:
            raise NetworkConnectionError(*e.args)

    def postprocess(self, resp, mail, url_events=None):
        status_code = resp.status_code
        if status_code in [200, 202]:
            post_event_url(
                url_events,
                build_event(
                    created_by=self.name(), event='DONE',
                    mail_id=mail.id,
                    blob=json.dumps({'status_code':resp.status_code})))

            return True

        post_event_url(url_events,
            build_event(
                created_by=self.name(), event='FAILURE',
                mail_id=mail.id,
                blob=json.dumps(
                {
                    'status_code':resp.status_code,
                    'body': resp.body
                })))

        details = resp.status_code, resp.reason, resp.text
        if status_code == 400:
            raise ValidationError(*details)
        elif status_code == 401:
            raise InvalidKey(*details)
        elif status_code == 402:
            raise PaymentRequired(*details)
        else:
            raise MailServiceException(*details)
        

