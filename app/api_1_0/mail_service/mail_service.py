import abc
import json
import requests
from ..utils import post_event_url, build_event
from .exceptions import *


class MailService(object):
    """ Abstract Class to model a Mail Service Provider

    """

    __metaclass__ = abc.ABCMeta

    def name(self):
        """Get the service name.

        Returns:
            str: short name of the service
        """

        return self.service_name

    def full_name(self):
        """Get the full service identifier in the form
            <service_name>:<unique_id>

        Returns:
            str: full name of the service
        """

        return ("%s:%s")% (self.service_name, self.id)

    def send(self, mail, url_events=None):
        """Send an email

        Args:
            mail (Mail): an instance of the class Mail
            url_events(str): an url to send event update.
                Defaults to None.

        Raises:
            MailServiceException            
        """

        try:
            for recipient in mail.recipients():
                message = self.prepare_message(mail.sender(), mail.subject(), recipient, mail.content())
                post_event_url(
                    url_events,
                    build_event(
                        created_by=self.full_name(),
                        event='SEND',
                        mail_id=mail.id,
                        blob=json.dumps({'to': recipient})))
                response = self.send_message(message)
                self.post_process(response=response, mail=mail, url_events=url_events)
            return True
        except ValidationError as e:
            post_event_url(
                url_events,
                build_event(
                    created_by=self.full_name(),
                    event='FAILURE',
                    mail_id=mail.id,
                    blob=json.dumps({'validation error': str(e.args)})))
            raise e
        except requests.exceptions.RequestException as e:
            post_event_url(
                url_events,
                build_event(
                    created_by=self.full_name(),
                    event='FAILURE',
                    mail_id=mail.id,
                    blob=json.dumps({'mail service error': str(e.args)})))
            raise MailServiceException(*e.args)
        except Exception as e:
            post_event_url(
                url_events,
                build_event(
                    created_by=self.full_name(),
                    event='FAILURE',
                    mail_id=mail.id,
                    blob=json.dumps({'network connection error': str(e.args)})))
            raise NetworkConnectionError(*e.args)

    def post_process(self, response, mail, url_events=None):
        """Validate the Mail provider response.

        Args:
            response(Response): a Response object as returned by a
                call to request.post
            mail (Mail): an instance of the class Mail
            url_events(str): an url to send events update.
                Defaults to None.

        Raises:
            MailServiceException
        """
        details = self.response_details(response)
        if details['status_code'] in [200, 202]:
            post_event_url(
                url_events,
                build_event(
                    created_by=self.full_name(),
                    event='DONE',
                    mail_id=mail.id,
                    blob=json.dumps(details)))
            return True

        post_event_url(
            url_events,
            build_event(
                created_by=self.full_name(),
                event='FAILURE',
                mail_id=mail.id,
                blob=json.dumps(self.details)))

        if details['status_code'] == 400:
            raise ValidationError(*details)
        elif details['status_code'] == 401:
            raise InvalidKey(*details)
        elif details['status_code'] == 402:
            raise PaymentRequired(*details)
        else:
            raise MailServiceException(*details)

    @abc.abstractmethod
    def response_details(self, response):
        """Extract response details.

        Args:
            response(Response): a Response object as returned by a
                call to request.post

        Returns:
            dict: a dictionary with response details,
            e.g.
                {
                    'status_code':resp.status_code,
                    'reason': resp.reason,
                    'text':resp.text
                }
        """
        pass

    @abc.abstractmethod
    def prepare_message(self, sender, subject, recipient, content):
        """Prepare the mail message.
        This is a specific action depending on the Mail Service Provider.

        Args:
            sender(str): sender mail address
            subject(str): subject of this message
            recipient(str): recipient mail address
            content(str): message body

        Returns:
            message(Object): a mail object

        Raises:
            ValidationError
        """
        pass

    @abc.abstractmethod
    def send_message(self, message):
        """Prepare the mail message.
        This is a specific action depending on the Mail Service Provider.

        Args:
            message(Object): a mail object returned by prepare_message()

        Raises:
            MailServiceException
        """
        pass
