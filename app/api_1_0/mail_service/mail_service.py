import abc

class MailServiceException(Exception):
    pass

class InvalidKey(MailServiceException):
    pass

class PaymentRequired(MailServiceException):
    pass

class ValidationError(MailServiceException):
    pass

class NetworkConnectionError(MailServiceException):
    pass

class MailService(object):
    """ Model a Generic Mail Service

    """
    __metaclass__ = abc.ABCMeta


    @abc.abstractmethod
    def name(self):
        """Get the service identifier.

        Returns:
            str: the service identifier
        """

        pass

    @abc.abstractmethod
    def send(self, mail, url_events=None):
        """Send an email

        Args:
            mail (Mail): an instance of the class Mail
            url_events(str): an url to send event update.
                Defaults to None.

        Raises:
            MailServiceException            
        """
        pass

    @abc.abstractmethod
    def postprocess(self, resp, mail, url_events=None):
        """Check for errors in the response.
        
        Args:
            resp(Response): a Response object as returned by a
                call to request.post
            mail (Mail): an instance of the class Mail
            url_events(str): an url to send events update.
                Defaults to None.

        Raises:
            MailServiceException  
        """
        pass