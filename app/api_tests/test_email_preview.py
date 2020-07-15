import unittest
from json import dumps
from json.decoder import JSONDecodeError
from requests.exceptions import ConnectionError
import json
from app.api_tests.test_message_create_apis import app
from bson import ObjectId



class AllTestMailsettingApis(unittest.TestCase):

    def setUp(self):
        app.testing = True
        self.app = app.test_client()

    def tearDown(self):
        pass

    def json_of_response(self, response):
        return json.loads(response.data.decode('utf8'))


    #testing send mail test api
    def test_send_mail_api(self):
        payload = json.dumps({
            "message": "This is api test cases testing",
            "subject": "Test cases Testing",
            "to": ["aayush_saini@excellencetechnologies.in"]
        })

        #act
        response = self.app.post('/notify/send_mail',headers={"Content-Type": "application/json"}, data=payload)

        # assert
        self.assertEqual(response.status_code, 200)
        self.assertIn('Sended',response.get_data(as_text=True))


    #testing send mail api
    def test_send_mail_api_to_not_available(self):
        payload = json.dumps({
            "message": "This is api test cases testing",
            "subject": "Test cases Testing"
        })

        #act
        response = self.app.post('/notify/send_mail',headers={"Content-Type": "application/json"}, data=payload)

        # assert
        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid Request',response.get_data(as_text=True))


    #testing send mail api if message not available
    def test_send_mail_api_message_not_available(self):
        payload = json.dumps({
            "subject": "Test cases Testing",
            "to":["aayush_saini@excellencetechnologies.in"]
        })

        #act
        response = self.app.post('/notify/send_mail',headers={"Content-Type": "application/json"}, data=payload)

        # assert
        self.assertEqual(response.status_code, 400)
        self.assertIn('Message subject and recipents not should be none',response.get_data(as_text=True))


    #testing get mail settings test api
    def test_get_mail_settings(self):
        payload = json.dumps({
            "email": "testnt64@gmail.com"
        })

        #act
        response = self.app.post('/notify/mail_test',headers={"Content-Type": "application/json"}, data=payload)

        # assert
        self.assertEqual(response.status_code, 200)
        self.assertIn('Smtp working',response.get_data(as_text=True))


    #testing mail template requirements test api
    def test_email_template_requirement(self):
        message_key = "first_round"

        #act
        response = self.app.get('/notify/email_template_requirement/'+message_key)
        #assert
        self.assertEqual(response.status_code, 200)
