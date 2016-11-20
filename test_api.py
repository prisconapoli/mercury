import unittest
import json
from app import create_app
from app import db
from app.api_1_0.mail.models import Mail
from app.api_1_0.event.models import Event
from app.api_1_0.mail_dispatcher.worker import process_message
from app.api_1_0.mail_dispatcher import mail_services, get_mail_service
from app.api_1_0.mail_dispatcher.exceptions import Retry, MailServiceNotAvailable


class TestApi(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.drop_all()
        db.create_all()
        self.client = self.app.test_client()
        self.headers = {'Content-Type': 'application/json'}
        self.base_url = 'http://localhost:5000/api/v1.0/'
        self.sender = 'mercury@olimpus.com'
        self.recipient = 'zeus@olimpus.com'
        self.message = {
            'sender': self.sender,
            'recipient': self.recipient,
            'subject': 'Story of Circe and Odysseus',
            'content': 'Then I went back to high Olympus passing over the wooded island...'
        }

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_endpoints(self):
        response = self.client.get(
            self.base_url,
            headers=self.headers)
        self.assertTrue(response.status_code == 200)

    def test_new_email(self):


        response = self.client.post(
            self.base_url + 'mails/',
            data=json.dumps(self.message), headers=self.headers)

        self.assertTrue(response.status_code == 202)
        location = response.headers.get('Location')
        self.assertIsNotNone(location)

        response = self.client.get(
            location,
            headers=self.headers)
        self.assertTrue(response.status_code == 200)
        mail = json.loads(response.data.decode('utf-8'))
        self.assertTrue(mail['sender'] == self.message['sender'])
        self.assertTrue(mail['recipient'] == self.message['recipient'])
        self.assertTrue(mail['subject'] == self.message['subject'])
        self.assertTrue(mail['content'] == self.message['content'])
        self.assertIsNotNone(mail['url'])

    def test_mandatory_fields(self):
        message1 = {
            'sender': '',
            'recipient': 'prisco.napoli@gmail.com',
            'subject': 'subject',
            'content': 'content'
        }

        message2 = {
            'sender': 'prisco.napoli@gmail.com',
            'recipient': '',
            'subject': 'subject',
            'content': 'content'
        }

        response = self.client.post(
            self.base_url + 'mails/',
            data=json.dumps(message1), headers=self.headers)

        self.assertTrue(response.status_code == 400)

        response = self.client.post(
            self.base_url + 'mails/',
            data=json.dumps(message2), headers=self.headers)
        self.assertTrue(response.status_code == 400)

    def test_sender_limit(self):
        sender = 'a' * (Mail.MaxSenderLen + 1)
        message = {
            'sender': sender,
            'recipient': self.recipient,
            'subject': 'subject',
            'content': 'content'
        }

        response = self.client.post(
            self.base_url + 'mails/',
            data=json.dumps(message), headers=self.headers)
        self.assertTrue(response.status_code == 400)

    def test_sender_limit(self):
        recipient = 'a' * (Mail.MaxRecipientLen + 1)
        message = {
            'sender': self.sender,
            'recipient': recipient,
            'subject': 'subject',
            'content': 'content'
        }

        response = self.client.post(
            self.base_url + 'mails/',
            data=json.dumps(message), headers=self.headers)
        self.assertTrue(response.status_code == 400)

        response = self.client.post(
            self.base_url + 'mails/',
            data=json.dumps(message), headers=self.headers)
        self.assertTrue(response.status_code == 400)

    def test_subject_limit(self):
        subject = 'a' * (Mail.MaxSubjectLen + 1)
        message = {
            'sender': self.sender,
            'recipient': self.recipient,
            'subject': subject,
            'content': 'content'
        }

        response = self.client.post(
            self.base_url + 'mails/',
            data=json.dumps(message), headers=self.headers)
        self.assertTrue(response.status_code == 400)

    def test_content_limit(self):
        content = 'a' * (Mail.MaxContentLen + 1)
        message4 = {
            'sender': self.sender,
            'recipient': self.recipient,
            'subject': 'subject',
            'content': content
        }

        response = self.client.post(
            self.base_url + 'mails/',
            data=json.dumps(message4), headers=self.headers)
        self.assertTrue(response.status_code == 400)

    def test_email_not_found(self):
        mail_id = 1
        response = self.client.get(
            self.base_url + 'mails/'+ str(mail_id), headers=self.headers)
        self.assertTrue(response.status_code == 404)

    def test_mail_events(self):
        response = self.client.post(
            self.base_url + 'mails/',
            data=json.dumps(self.message), headers=self.headers)

        self.assertTrue(response.status_code == 202)
        location = response.headers.get('Location')
        self.assertIsNotNone(location)
        response = self.client.get(
            location,
            headers=self.headers)
        self.assertTrue(response.status_code == 200)
        mail = json.loads(response.data.decode('utf-8'))
        self.assertIsNotNone(mail['events'])
        events = mail['events']
        response = self.client.get(
            events,
            headers=self.headers)
        self.assertTrue(response.status_code == 200)

    def test_pagination(self):
        response = self.client.post(
            self.base_url + 'mails/',
            data=json.dumps(self.message), headers=self.headers)

        self.assertTrue(response.status_code == 202)
        location = response.headers.get('Location')
        self.assertIsNotNone(location)
        response = self.client.get(
            location,
            headers=self.headers)
        self.assertTrue(response.status_code == 200)
        mail = json.loads(response.data.decode('utf-8'))
        self.assertIsNotNone(mail['events'])
        response = self.client.get(
            mail['url'],
            headers=self.headers)
        self.assertTrue(response.status_code == 200)
        mail = json.loads(response.data.decode('utf-8'))
        self.assertEqual(mail['sender'], self.message['sender'])
        self.assertEqual(mail['recipient'], self.message['recipient'])
        self.assertEqual(mail['subject'], self.message['subject'])
        self.assertEqual(mail['content'], self.message['content'])

        response = self.client.get(
            mail['events'],
            headers=self.headers)
        mail = json.loads(response.data.decode('utf-8'))

        first_url = mail['meta']['first_url']
        self.assertIsNotNone(first_url)
        response = self.client.get(
            first_url,
            headers=self.headers)
        self.assertTrue(response.status_code == 200)
        mail = json.loads(response.data.decode('utf-8'))
        last_url = mail['meta']['last_url']
        self.assertIsNotNone(last_url)
        response = self.client.get(
            last_url,
            headers=self.headers)
        self.assertTrue(response.status_code == 200)
        next_url = mail['meta']['next_url']
        self.assertIsNone(next_url)

    def test_sendgrind_worker(self):
        mail = Mail.from_dict(self.message)
        attempts = []
        process_message('test', mail, mail_services['Sendgrid'][0], attempts)

    def test_mailgun_worker(self):
        mail = Mail.from_dict(self.message)
        attempts = []
        self.assertRaises(Retry, process_message,'test', mail, mail_services['Mailgun'][0], attempts)

    def test_mail_service_none(self):
        mail = Mail.from_dict(self.message)
        attempts = []
        self.assertRaises(MailServiceNotAvailable, process_message, 'test', mail, None, attempts)

    def test_mail_service_not_available(self):
        attempts = []
        for service in mail_services.keys():
            attempts.append(service)
        service = get_mail_service(attempts)
        self.assertIsNone(service)

    def test_put_event(self):
        mail = Mail.from_dict(self.message)
        db.session.add(mail)
        db.session.flush()
        db.session.commit()

        event_dict = {
            'created_at': 12345,
            'created_by': 'test',
            'event': 'test',
            'mail_id': str(mail.id),
            'blob': "{test : 'test data'}"
        }
        event = Event.from_dict(event_dict)
        db.session.add(event)
        db.session.flush()
        db.session.commit()
        response = self.client.post(
            self.base_url + 'mails/' + str(mail.id) + '/events/',
            data=json.dumps(event_dict),
            headers=self.headers)
        self.assertTrue(response.status_code == 201)

    def test_get_event(self):
        mail = Mail.from_dict(self.message)
        db.session.add(mail)
        db.session.flush()
        db.session.commit()

        event_dict = {
            'created_at': 12345,
            'created_by': 'test',
            'event': 'test',
            'mail_id': str(mail.id),
            'blob': "{test : 'test data'}"
        }
        event = Event.from_dict(event_dict)
        db.session.add(event)
        db.session.flush()
        db.session.commit()
        response = self.client.get(
            self.base_url + 'mails/' + str(mail.id) + '/events/' + str(event.id), headers=self.headers)
        self.assertTrue(response.status_code == 200)

    def test_missing_mail(self):
        message = {
            'sender': self.sender,
            'recipient': self.recipient,
            'subject': 'Story of Circe and Odysseus',
            'content': 'Then I went back to high Olympus passing over the wooded island...'
        }

        mail = Mail.from_dict(message)
        db.session.add(mail)
        db.session.flush()
        db.session.commit()
        response = self.client.get(self.base_url + 'mails/' + str(mail.id + 1) + '/events/',
                                   headers=self.headers)
        self.assertTrue(response.status_code == 404)

    def test_missing_event(self):
        message = {
            'sender': self.sender,
            'recipient': self.recipient,
            'subject': 'Story of Circe and Odysseus',
            'content': 'Then I went back to high Olympus passing over the wooded island...'
        }

        mail = Mail.from_dict(message)
        db.session.add(mail)
        db.session.flush()
        db.session.commit()

        event_dict = {
            'created_at': 12345,
            'created_by': 'test',
            'event': 'test',
            'mail_id': str(mail.id),
            'blob': "{test : 'test data'}"
        }
        event = Event.from_dict(event_dict)
        db.session.add(event)
        db.session.flush()
        db.session.commit()
        response = self.client.get(self.base_url + 'mails/' + str(mail.id) + '/events/' + str(event.id+1),
                                   headers=self.headers)
        self.assertTrue(response.status_code == 404)

if __name__ == '__main__':
    unittest.main()
