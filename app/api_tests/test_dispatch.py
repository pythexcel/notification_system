
import unittest
from json import dumps
from json.decoder import JSONDecodeError
from requests.exceptions import ConnectionError
import json
from app.api_tests.test_message_create_apis import app
from bson import ObjectId
from app import mongo
from app.config import account_name,secret_key
'''
class AllTestMailsettingApis(unittest.TestCase):

    def setUp(self):
        app.testing = True
        self.app = app.test_client()

    def tearDown(self):
        pass

    def json_of_response(self, response):
        return json.loads(response.data.decode('utf8'))
    #Note: commented this test case because can't upload slack token on git it will expire
    
    def create_slack_setting(self):
        payload = {"slack_token":""}
        mongo.db.slack_settings.insert_one(payload) 

    #testing slack token test api
    def test_slack_token_test_api(self):
        #making data
        self.create_slack_setting()

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
        notfication_msg={"message_key":"user_timesheet_entry","channels":"public","email_group":None,"for_email":False,"for_phone":False,"for_slack":False,"for_zapier":True,"message":"you have made a entry on timesheet \n Date : @date: \n Hours: @hours:","message_color":None,"message_origin":"HR","message_type":"simple_message","sended_to":"public","slack_channel":["CHVFM6U30"],"submission_type":"HR","working":True}
        mongo.db.notification_msg.insert_one(notfication_msg)


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
        response = self.app.post('/notify/dispatch?account-name='+account_name,headers={"Content-Type": "application/json"}, data=payload)

        # assert
        self.assertEqual(response.status_code, 200)
        self.assertIn('Sended',response.get_data(as_text=True))
        self.assertIn('true',response.get_data(as_text=True))
    

    #testing slack dispatch notification api invalid payload
    def test_slack_dispatch_notification_api_with_invalid_payload(self):
        notfication_msg={"message_key":"user_timesheet_entry","channels":"public","email_group":None,"for_email":False,"for_phone":False,"for_slack":False,"for_zapier":True,"message":"you have made a entry on timesheet \n Date : @date: \n Hours: @hours:","message_color":None,"message_origin":"HR","message_type":"simple_message","sended_to":"public","slack_channel":["CHVFM6U30"],"submission_type":"HR","working":True}
        mongo.db.notification_msg.insert_one(notfication_msg)
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
'''