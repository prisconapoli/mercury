import unittest
import json
from app import create_app
from app import db
from app.api_1_0.mail.models import Mail


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
        message = {
            'sender': self.sender,
            'recipient': self.recipient,
            'subject': 'Story of Circe and Odysseus',
            'content': 'Then I went back to high Olympus passing over the wooded island...'
        }

        response = self.client.post(
            self.base_url + 'mails/',
            data=json.dumps(message), headers=self.headers)

        self.assertTrue(response.status_code == 202)
        location = response.headers.get('Location')
        self.assertIsNotNone(location)

        response = self.client.get(
            location,
            headers=self.headers)
        self.assertTrue(response.status_code == 200)
        mail = json.loads(response.data.decode('utf-8'))
        self.assertTrue(mail['sender'] == message['sender'])
        self.assertTrue(mail['recipient'] == message['recipient'])
        self.assertTrue(mail['subject'] == message['subject'])
        self.assertTrue(mail['content'] == message['content'])
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
        message = {
            'sender': self.sender,
            'recipient': self.recipient,
            'subject': 'Story of Circe and Odysseus',
            'content': 'Then I went back to high Olympus passing over the wooded island...'
        }

        response = self.client.post(
            self.base_url + 'mails/',
            data=json.dumps(message), headers=self.headers)

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
        message = {
            'sender': self.sender,
            'recipient': self.recipient,
            'subject': 'Story of Circe and Odysseus',
            'content': 'Then I went back to high Olympus passing over the wooded island...'
        }

        response = self.client.post(
            self.base_url + 'mails/',
            data=json.dumps(message), headers=self.headers)

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
        self.assertEqual(mail['sender'], message['sender'])
        self.assertEqual(mail['recipient'], message['recipient'])
        self.assertEqual(mail['subject'], message['subject'])
        self.assertEqual(mail['content'], message['content'])

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

if __name__ == '__main__':
    unittest.main()
