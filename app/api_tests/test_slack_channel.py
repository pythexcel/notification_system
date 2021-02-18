'''
import unittest
from json import dumps
from json.decoder import JSONDecodeError
from requests.exceptions import ConnectionError
import json
from app.api_tests.test_message_create_apis import app
from bson import ObjectId
from app import mongo


class AllTestslackchannelApis(unittest.TestCase):

    def setUp(self):
        app.testing = True
        self.app = app.test_client()

    def tearDown(self):
        pass

    def json_of_response(self, response):
        return json.loads(response.data.decode('utf8'))
        
    #Note: commented these test cases based on slack token can't upload slack token on repo
    def create_slack_setting(self):
        payload = {"slack_token":}
        mongo.db.slack_settings.insert_one(payload) 


    #testing slack channels get api
    def test_slack_channel_test_api(self):
        #making data
        self.create_slack_setting()

        #act
        response = self.app.get('/slackchannels')
        jsonResponse = self.json_of_response(response)

        # assert
        self.assertEqual(response.status_code, 200)
        self.assertIn('Private_channel',response.get_data(as_text=True))
        self.assertIn('Public_channel',response.get_data(as_text=True))



    #testing slack get user private channel api
    def test_get_slack_user_private_channels(self):
        #data making
        self.create_slack_setting()

        payload = json.dumps({
                "email":"aayush_saini@excellencetechnologies.in"
                })

        #act
        response = self.app.post('/slackchannels',headers={"Content-Type": "application/json"}, data=payload)
        jsonResponse = self.json_of_response(response)

        # assert
        self.assertEqual(response.status_code, 200)



    #testing slack get user profile  api
    def test_get_slack_user_profile_api(self):
        #data making
        self.create_slack_setting()

        payload = json.dumps({
                "email":"aayush_saini@excellencetechnologies.in"
                })

        #act
        response = self.app.post('/slack_profile',headers={"Content-Type": "application/json"}, data=payload)
        jsonResponse = self.json_of_response(response)

        # assert
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(jsonResponse),0)


    #testing get slack channels IDs
    def test_get_slack_channels_ids(self):
        #data making
        self.create_slack_setting()

        #act
        response = self.app.get('/slack_channel_ids')
        jsonResponse = self.json_of_response(response)
        # assert
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(jsonResponse),0)


    #testing get slack user list
    def test_get_slack_user_list(self):
        #data making
        self.create_slack_setting()

        #act
        response = self.app.get('/slack_users_list')
        jsonResponse = self.json_of_response(response)
        # assert
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(jsonResponse),0)


    #testing get slack settings
    def test_get_slack_settings(self):

        #data making
        self.create_slack_setting()

        #act
        response = self.app.get('/slack/settings')
        jsonResponse = self.json_of_response(response)
        # assert
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(jsonResponse),0)
    """


    #testing put slack settings
    def test_put_slack_settings(self):

        payload = json.dumps({
                "slack_token":"xoxb-124720392913-12444231729-psBtbRa6d0d01Cu04me3Ekyn"
                })

        #act
        response = self.app.put('/slack/settings',headers={"Content-Type": "application/json"}, data=payload)
        jsonResponse = self.json_of_response(response)

        # assert
        self.assertEqual(response.status_code, 200)
        self.assertIn('upserted',response.get_data(as_text=True))



    #testing put slack settings if slack token not available
    def test_put_slack_settings_invalid_payload(self):

        payload = json.dumps({
                "slack_token":None
                })

        #act
        response = self.app.put('/slack/settings',headers={"Content-Type": "application/json"}, data=payload)
        jsonResponse = self.json_of_response(response)

        # assert
        self.assertEqual(response.status_code, 400)
        self.assertIn('Slack Token missing',response.get_data(as_text=True))
'''