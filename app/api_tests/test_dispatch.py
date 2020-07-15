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


    #testing slack token test api
    def test_slack_token_test_api(self):
        payload = json.dumps({
                "email":"aayush_saini@excellencetechnologies.in"
                })

        #act
        response = self.app.post('/notify/slack_test',headers={"Content-Type": "application/json"}, data=payload)

        # assert
        self.assertEqual(response.status_code, 200)
        self.assertIn('Slack Token Tested',response.get_data(as_text=True))
        self.assertIn('true',response.get_data(as_text=True))


    #testing slack token test api with invalid payload
    def test_slack_token_test_api_if_token_not_valid(self):
        payload = json.dumps({
                "email":"aayush_saini@excellenceechologies.in"
                })

        #act
        response = self.app.post('/notify/slack_test',headers={"Content-Type": "application/json"}, data=payload)

        # assert
        self.assertEqual(response.status_code, 400)
        self.assertIn('Slack User not exist or invalid token',response.get_data(as_text=True))
        self.assertIn('false',response.get_data(as_text=True))



    #testing slack dispatch notification api
    def test_slack_dispatch_notification_api(self):
        payload = json.dumps({
                            "message_key": "user_timesheet_entry",
                            "message_type": "simple_message",
                            "user": {
                                "email": "aayush_saini@excellencetechnologies.in",
                                "name":"aayush"
                            },
                            "data": {
                                "hours": "9",
                                "date": "Friday, June 5th 2020, 2:15:49 pm"
                            },
                            "emailData":{
                                "subject":"testing"
                            },
                            "PhoneData":{
                                "phoneno":"8445679788"
                            },
                            "email_group":["aayush_saini@excellencetechnologies.in"]
                        })

        #act
        response = self.app.post('/notify/dispatch',headers={"Content-Type": "application/json"}, data=payload)

        # assert
        self.assertEqual(response.status_code, 200)
        self.assertIn('Sended',response.get_data(as_text=True))
        self.assertIn('true',response.get_data(as_text=True))


    #testing slack dispatch notification api invalid payload
    def test_slack_dispatch_notification_api_with_invalid_payload(self):
        payload = json.dumps({
                            "message_key": "user_timesheet_entry",
                            "message_type": "simple_message",
                            "data": {
                                "hours": "9",
                                "date": "Friday, June 5th 2020, 2:15:49 pm"
                            },
                            "email_group":["aayush_saini@excellencetechnologies.in"]
                        })

        #act
        response = self.app.post('/notify/dispatch',headers={"Content-Type": "application/json"}, data=payload)

        # assert
        self.assertEqual(response.status_code,400)
