
import unittest
from json import dumps
from json.decoder import JSONDecodeError
from requests.exceptions import ConnectionError
import json
from app.api_tests.test_message_create_apis import app
from bson import ObjectId
from app import mongo
import datetime
from app.config import secret_key,account_name

class AllTestReminderApis(unittest.TestCase):

    def setUp(self):
        app.testing = True
        self.app = app.test_client()

    def tearDown(self):
        pass

    def json_of_response(self, response):
        return json.loads(response.data.decode('utf8'))

    #testing reminder details api
    def test_reminder_details(self):
        payload = {"date":datetime.datetime.today(),"message_key":"Interview Reminder","jobId":"123"}
        mongo.db.reminder_details.insert_one(payload)

        #act
        response = self.app.get('/notify/reminder_details/123?account-name='+account_name,headers={"Secretkey":str(secret_key)})
        jsonResponse = self.json_of_response(response)

        # assert
        self.assertEqual(response.status_code, 200)
        self.assertIn('total',jsonResponse)


