import unittest
from unittest.mock import patch, Mock
from json import dumps
from json.decoder import JSONDecodeError
from requests.exceptions import ConnectionError
import json
from app import create_app

app = create_app()
app.app_context().push()


class AllDataTestCase(unittest.TestCase):

    def setUp(self):
        app.testing = True
        self.app = app.test_client()

    def tearDown(self):
        pass

    def json_of_response(self, response):
        return json.loads(response.data.decode('utf8'))


    def test_special_variables(self):

        # act
        response = self.app.get('/message/special_variable')
        jsonResponse = self.json_of_response(response)
        # assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list,type(jsonResponse))
        self.assertGreater(len(jsonResponse),0)
        self.assertIn('_id', response.get_data(as_text=True))
        self.assertIn('name', response.get_data(as_text=True))
        self.assertIn('value', response.get_data(as_text=True))
        self.assertIn('variable_type', response.get_data(as_text=True))


    def test_put_special_variables(self):
        payload = json.dumps({
            "name": "test_name",
            "value": "test_value",
            "variable_type": "test_variable_type"
        })
        # act
        response = self.app.put('/message/special_variable',headers={"Content-Type": "application/json"}, data=payload)

        # assert
        self.assertEqual(response.status_code, 200)


    def test_get_notification_message(self):

        message_origin = "TMS"
        
        # act
        response = self.app.get(f'/message/configuration/'+message_origin)
        jsonResponse = self.json_of_response(response)[0]

        # assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(dict,type(jsonResponse))
        self.assertGreater(len(jsonResponse),0)
        self.assertIn('message', jsonResponse)
        self.assertIn('message_key', jsonResponse)
        self.assertIn('message_origin', jsonResponse)
        self.assertIn('message_type', jsonResponse)
        self.assertIn('sended_to', jsonResponse)
        self.assertIn('slack_channel', jsonResponse)


