import unittest
import json
import requests
from app import create_app
from app.api_1_0.models import db, Mail, Event
from app.api_1_0.errors import ValidationError

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

    def test_invalid_email(self):
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

        sender = 'a' * (Mail.MaxSenderLen + 1)  
        message3 = {
            'sender': sender,
            'recipient': self.recipient, 
            'subject': 'subject',
            'content': 'content'
        }

        recipient = 'a' * (Mail.MaxRecipientLen + 1) 
        message4 = {
            'sender': self.sender,
            'recipient': recipient, 
            'subject': 'subject',
            'content': 'content'
        }

        subject = 'a' * (Mail.MaxSubjectLen + 1) 
        message5 = {
            'sender': self.sender,
            'recipient': self.recipient, 
            'subject': subject,
            'content': 'content'
        }

        content = 'a' * (Mail.MaxContentLen + 1) 
        message6 = {
            'sender': self.sender,
            'recipient': self.recipient, 
            'subject': 'subject',
            'content': content
        }

        response = self.client.post(
            self.base_url + 'mails/',
            data=json.dumps(message1), headers=self.headers)
        self.assertTrue(response.status_code == 400)

        response = self.client.post(
            self.base_url + 'mails/',
            data=json.dumps(message2), headers=self.headers)
        self.assertTrue(response.status_code == 400)

        response = self.client.post(
            self.base_url + 'mails/',
            data=json.dumps(message3), headers=self.headers)
        self.assertTrue(response.status_code == 400)

        response = self.client.post(
            self.base_url + 'mails/',
            data=json.dumps(message4), headers=self.headers)
        self.assertTrue(response.status_code == 400)

        response = self.client.post(
            self.base_url + 'mails/',
            data=json.dumps(message5), headers=self.headers)
        self.assertTrue(response.status_code == 400)

        response = self.client.post(
            self.base_url + 'mails/',
            data=json.dumps(message6), headers=self.headers)
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
        mail = json.loads(response.data.decode('utf-8'))

if __name__ == '__main__':
    unittest.main()