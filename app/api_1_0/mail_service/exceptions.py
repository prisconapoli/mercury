class MailServiceException(Exception):
    pass


class ValidationError(MailServiceException):
    pass


class InvalidKey(MailServiceException):
    pass


class PaymentRequired(MailServiceException):
    pass


class NetworkConnectionError(MailServiceException):
    pass
