from ..utils import post_event_url,build_event
from .mail_service import *
from mail_config import MailConfig
import requests
import uuid
import json
import requests

class MailgunService(MailService):
    """ Send email using Mailgun Service.

    This is a concrete class that inherits from MailService
    It requires the definition of these properties:
        MAILGUN_URL_API
        MAILGUN_DOMAIN_NAME
        MAILGUN_API_KEY
    """

    Name = 'Mailgun'
    def __init__(self):
        self.id = str(uuid.uuid4())

    def name(self):

        return MailgunService.Name + ":" + self.id 

    def send(self, mail, url_events=None):
        url = MailConfig.MAILGUN_URL_API.format(MailConfig.MAILGUN_DOMAIN_NAME)
        auth = ('api', MailConfig.MAILGUN_API_KEY)
        data = {
            'from': mail.get_sender(),
            'to': mail.get_recipient(),
            'subject': mail.get_subject(),
            'text': mail.get_content(),
        }

        try:
            post_event_url(url_events, build_event(created_by=self.name(), \
                event='SEND', mail_id=mail.id))

            response=requests.post(url, auth=auth, data=data)
            return self.postprocess(resp=response, mail=mail, url_events=url_events)
        except requests.exceptions.RequestException as e:
            raise MailServiceException(*e.args)
        except Exception as e:
            raise NetworkConnectionError(*e.args)

    def postprocess(self, resp, mail, url_events=None):
        if resp.status_code in [200, 202]:
            post_event_url(
                url_events,
                build_event(
                    created_by=self.name(), event='DONE',
                    mail_id=mail.id,
                    blob=json.dumps({
                        'status_code':resp.status_code,
                        'reason': resp.reason,
                        'text':resp.text
                        })))
            return True

        post_event_url(
            url_events,
            build_event(
            created_by=self.name(), event='FAILURE',
            mail_id=mail.id,
            blob=json.dumps({
                'status_code':resp.status_code,
                'reason': resp.reason,
                'text':resp.text
                })))

        details = resp.status_code, resp.reason, resp.text
        if resp.status_code == 400:
            raise ValidationError(*details)
        elif resp.status_code == 401:
            raise InvalidKey(*details)
        elif resp.status_code == 402:
            raise PaymentRequired(*details)
        else:
            raise MailServiceException(*details)