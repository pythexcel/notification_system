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

    #testing get mail setting api
    def test_get_mail_settings(self):

        origin = "HR"
        #act
        response = self.app.get('/smtp/settings/'+origin)
        jsonResponse = self.json_of_response(response)

        self.assertEqual(response.status_code, 200)
        for jsonResponses in jsonResponse:
            # assert
            self.assertIn('_id',jsonResponses)
            self.assertIn('active',jsonResponses)
            self.assertIn('created_at',jsonResponses)
            self.assertIn('mail_from',jsonResponses)
            self.assertIn('mail_port',jsonResponses)
            self.assertIn('mail_server',jsonResponses)
            self.assertIn('mail_use_tls',jsonResponses)
            self.assertIn('mail_username',jsonResponses)
            self.assertIn('origin',jsonResponses)
            self.assertIn('priority',jsonResponses)
            self.assertIn('type',jsonResponses)


    #testing delete mail settings api
    def test_delete_mail_settings(self):
        origin = "test"
        id = "5e302e8a0058741d4a7c1ea0" 
        #act
        response = self.app.delete('/smtp/settings/'+origin+'/'+id)

        self.assertEqual(response.status_code, 200)
        self.assertIn('Smtp conf deleted',response.get_data(as_text=True))



    #testing update mail settings api
    def test_update_mail_settings(self):
        origin = "test"
        id = "5e302e8a0058741d4a7c1ea0" 
        payload = json.dumps({
            "active": True
        })

        #act
        response = self.app.put('/smtp/settings/'+origin+'/'+id,headers={"Content-Type": "application/json"}, data=payload)

        self.assertEqual(response.status_code, 200)
        self.assertIn('Smtp conf status changed',response.get_data(as_text=True))


    #testing smtp priority api
    def test_smtp_priority(self):
        position = "1"
        Id = "5e302e8a0058741d4a7c1ea0" 

        #act
        response = self.app.post('/smtp/smtp_priority/'+Id+'/'+position)

        self.assertEqual(response.status_code, 200)
        self.assertIn("priority changed",response.get_data(as_text=True))


    def test_update_settings_with_invalid_payload(self):
        origin = "test"
        id = "5e302e8a0058741d4a7c1ea0" 
        payload = json.dumps({
            "new_password":"asdasdaas"
        })

        #act
        response = self.app.put('/smtp/update_settings/'+origin+'/'+id,headers={"Content-Type": "application/json"}, data=payload)

        self.assertEqual(response.status_code, 400)
        self.assertIn("No smtp exists",response.get_data(as_text=True))


    #testing validate smtp api
    def test_validate_smtp(self):
        payload = json.dumps({
            "email":"testnt64@gmail.com",
            "password":"injbjnzckuqjddgm"
            })

        #act
        response = self.app.post('/smtp/validate_smtp',headers={"Content-Type": "application/json"}, data=payload)

        self.assertEqual(response.status_code, 200)
        self.assertIn("login succesfull",response.get_data(as_text=True))


    #testing validate smtp api with invalid crediantials
    def test_validate_smtp_invalid_crediantials(self):
        payload = json.dumps({
            "email":"testnt64@gmail.com",
            "password":"injbjnzcuqjddgm"
            })

        #act
        response = self.app.post('/smtp/validate_smtp',headers={"Content-Type": "application/json"}, data=payload)

        self.assertEqual(response.status_code, 400)
        self.assertIn("smtp login and password failed",response.get_data(as_text=True))
