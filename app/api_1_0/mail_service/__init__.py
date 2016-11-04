from .mailgun_service import MailgunService
from .sendgrid_service import SendgridService

mail_services = {
    'mailgun': MailgunService(),
    'sendgrid': SendgridService()
}
