import unittest
from json import dumps
from json.decoder import JSONDecodeError
from requests.exceptions import ConnectionError
import json
from app.api_tests.test_message_create_apis import app
from bson import ObjectId



class AllTestSettingApis(unittest.TestCase):

    def setUp(self):
        app.testing = True
        self.app = app.test_client()

    def tearDown(self):
        pass

    def json_of_response(self, response):
        return json.loads(response.data.decode('utf8'))

    #Test case for put test system setting
    def test_put_settings(self):
        payload = json.dumps({
                "pdf":True
            })

        # act
        response = self.app.put('/settings',headers={"Content-Type": "application/json"}, data=payload)

        # assert
        self.assertEqual(response.status_code, 200)
        self.assertIn('upserted',response.get_data(as_text=True))


    #Test case for get system setting api
    def test_get_settings(self):
        # act
        response = self.app.get('/settings')
        jsonResponse = self.json_of_response(response)

        # assert
        self.assertEqual(response.status_code, 200)
        self.assertIn('pdf',jsonResponse)
