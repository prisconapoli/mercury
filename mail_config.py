import os

basedir = os.path.abspath(os.path.dirname(__file__))

class MailConfig(object):
    SENDGRID_API_KEY=os.environ.get('SENDGRID_API_KEY') or \
        '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'

    MAILGUN_URL_API=os.environ.get('MAILGUN_URL_API') or \
        'https://api.mailgun.net/v3/{}/messages'

    MAILGUN_DOMAIN_NAME=os.environ.get('MAILGUN_DOMAIN_NAME') or \
        'sandbox29429dd5fdb349d8bcb02937daa829cc.mailgun.org'

    MAILGUN_API_KEY='key-b9becf325c1a9ceb9b6c020163e363cf'
