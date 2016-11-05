import os

basedir = os.path.abspath(os.path.dirname(__file__))

class MailConfig(object):
    SENDGRID_API_KEY=os.environ.get('SENDGRID_API_KEY')

    MAILGUN_URL_API=os.environ.get('MAILGUN_URL_API')

    MAILGUN_DOMAIN_NAME=os.environ.get('MAILGUN_DOMAIN_NAME')

    MAILGUN_API_KEY=os.environ.get('MAILGUN_API_KEY')
