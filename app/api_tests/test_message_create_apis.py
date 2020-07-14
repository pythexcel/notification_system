import unittest
from json import dumps
from json.decoder import JSONDecodeError
from requests.exceptions import ConnectionError
import json
from app import create_app
from bson import ObjectId

app = create_app()
app.app_context().push()


#class for all message creation apis test
class AllDataTestCase(unittest.TestCase):

    def setUp(self):
        app.testing = True
        self.app = app.test_client()

    def tearDown(self):
        pass

    def json_of_response(self, response):
        return json.loads(response.data.decode('utf8'))

    #testing for special variables api
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

    #Tesing for put special variable api
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
        self.assertIn('upsert',response.get_data(as_text=True))

    #Testing get notification api
    def test_get_notification_message(self):

        message_origin = "TEST"
        
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

    #Testing put notification message api
    def test_put_notification_message(self):

        message_origin = "TEST"
        
        #payload
        payload = json.dumps({
            "message": "test_messages",
            "message_key": "test_api",
            "message_type": "simple_message",
            "message_color": "#0365",
            "working": True,
            "submission_type": "test_submission_type",
            "slack_channel": ["CH276YH"],
            "email_group": None,
            "channels": ["#6757hff"],
            "sended_to": "private",
            "for_email": False,
            "for_slack": True,
            "for_phone": False,
            "for_zapier": True
        })

        # act
        response = self.app.put(f'/message/configuration/'+message_origin,headers={"Content-Type": "application/json"}, data=payload)
        
        # assert
        self.assertEqual(response.status_code, 200)
        self.assertIn('upsert',response.get_data(as_text=True))


    #Testing get email tempalate api
    def test_get_email_template(self):

        message_origin = "RECRUIT"
        
        # act
        response = self.app.get(f'/message/get_email_template/'+message_origin)
        jsonResponse = self.json_of_response(response)[0]

        # assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(dict,type(jsonResponse))
        self.assertGreater(len(jsonResponse),0)
        self.assertIn('Doc_type', jsonResponse)
        self.assertIn('for', jsonResponse)
        self.assertIn('message', jsonResponse)
        self.assertIn('message_key', jsonResponse)
        self.assertIn('message_origin', jsonResponse)
        self.assertIn('message_subject', jsonResponse)
        self.assertIn('recruit_details', jsonResponse)
        self.assertIn('template_variables', jsonResponse)
        self.assertIn('working', jsonResponse)


    #testing delete email template apis
    def test_delete_email_template(self):

        message_origin = "RECRUIT"
        payload = json.dumps({
            "message_key": "test_third_round"
        })
        
        # act
        response = self.app.delete(f'/message/get_email_template/'+message_origin,headers={"Content-Type": "application/json"}, data=payload)

        # assert
        self.assertEqual(response.status_code, 200)
        self.assertIn("Template Deleted",response.get_data(as_text=True))


    #testing delete attachment api
    def test_delete_attachment_file(self):
        id = "5dfc6108c837f7bc90ab3cbc"
        file_id = "72d741fb-f568-4659-b6c1-80f8ff2e0e4f"

        # act
        response = self.app.delete(f'/message/delete_file/'+id+'/'+file_id)

        # assert
        self.assertEqual(response.status_code, 200)
        self.assertIn("File deleted",response.get_data(as_text=True))


    #testing put letter head api
    def test_put_letter_head(self):

        #payload
        payload = json.dumps({
            "name": "test_letter_head",
            "header_value": '<p> <div id="header"> <div style="height: 5px; background-color: #4bb698;">&nbsp;</div> <div style="height: 8px; margin-top: 1px; background-color: #4bb698;">&nbsp;</div> <div style="height: 5px; margin-top: 1px; background-color: #4bb698;">&nbsp;</div> <br /> <div style="text-align: right; padding-right:40px"><img src="https://res.cloudinary.com/dp0y84e66/image/upload/v1568791251/logo.e5be347d_yf4q90.png" style="width: 150px;" /></div> </div>',
            "footer_value": '<div id="footer" style="bottom: 0; position: absolute; width: 100%;"><hr /> <div>ExcellenceTechnosoft Pvt Ltd</div> <div>CIN: U72200DL2010PTC205087</div> <div>Corp Office:C84-A, Sector 8,Noida, U.P. - 201301</div> <div>Regd Office: 328 GAGAN VIHAR IST MEZZAZINE,NEW DELHI-110051</div> <div style="height: 5px; margin-top: 5px; margin-bottom: 2px; background-color: #4bb698;">&nbsp;</div> </div>',
            "working": True
        })

        # act
        response = self.app.put(f'/message/letter_heads',headers={"Content-Type": "application/json"}, data=payload)
        
        # assert
        self.assertEqual(response.status_code, 200)
        self.assertIn("Letter Head Created",response.get_data(as_text=True))

    #testing get letter head api
    def test_get_letter_head(self):

        # act
        response = self.app.get(f'/message/letter_heads')
        jsonResponse = self.json_of_response(response)[0]

        # assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(dict,type(jsonResponse))
        self.assertGreater(len(jsonResponse),0)
        self.assertIn('footer_value', jsonResponse)
        self.assertIn('header_value', jsonResponse)
        self.assertIn('name', jsonResponse)
        self.assertIn('working', jsonResponse)


    #test case for delete letter head api
    def test_delete_letter_head(self):
        id = "5f0c13d83fbe9cf994667444"

        response = self.app.delete(f'/message/letter_heads/'+id)

        # assert
        self.assertEqual(response.status_code, 200)
        self.assertIn("Letter Head Deleted",response.get_data(as_text=True))


    #test case for assign letter head api
    def test_assign_letter_head(self):

        #payload
        template_id = "5dea40490356855a0b3200a0"
        letter_head_id = "5f0c16db3fbe9cf9946700df"

        # act
        response = self.app.put(f'/message/assign_letter_heads/'+template_id+'/'+letter_head_id)
        
        # assert
        self.assertEqual(response.status_code, 200)
        self.assertIn("Letter Head Added To Template",response.get_data(as_text=True))


    #Test case for trigger api
    def test_get_triggers(self):

        # act
        response = self.app.get(f'/message/triggers')
        jsonResponse = self.json_of_response(response)

        # assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(dict,type(jsonResponse))
        self.assertGreater(len(jsonResponse),0)
        self.assertIn('triggers', jsonResponse)


    #Test case for get email template api
    def test_get_email_templates(self):
        # act
        response = self.app.get(f'/message/get_email_template')
        jsonResponses = self.json_of_response(response)

        # assert
        self.assertEqual(response.status_code, 200)
        for jsonResponse in jsonResponses:
            self.assertIn('Doc_type', jsonResponse)
            self.assertIn('for', jsonResponse)
            self.assertIn('message', jsonResponse)
            self.assertIn('message_key', jsonResponse)
            self.assertIn('message_origin', jsonResponse)
            self.assertIn('message_subject', jsonResponse)
            self.assertIn('template_variables', jsonResponse)
            self.assertIn('working', jsonResponse)

