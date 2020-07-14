import unittest
from json import dumps
from json.decoder import JSONDecodeError
from requests.exceptions import ConnectionError
import json
from app.api_tests.test_message_create_apis import app
from bson import ObjectId


#class for all campaign test cases
class AllTestCampaignApis(unittest.TestCase):


    def setUp(self):
        app.testing = True
        self.app = app.test_client()


    def tearDown(self):
        pass

    #common function for convert bytes to json
    def json_of_response(self, response):
        return json.loads(response.data.decode('utf8'))

    #common function for create a dummy campaign for testing
    def create_campaign(self):
        payload = json.dumps({
            "campaign_name": "test_campaign",
            "campaign_description": "created_campaign_for_testing",
            "status": "Idel",
            "message": "test_message",
            "message_subject": "test_subject",
            "generated_from_recruit":True
        })

        response = self.app.post('/create_campaign',headers={"Content-Type": "application/json"}, data=payload)
        jsonResponse = self.json_of_response(response)
        return jsonResponse,response

    #common function for delete campaign by id
    def delete_campaign(self,id):
        response = self.app.delete(f'/delete_campaign/'+id)
        return response

    #test case for create campaign api
    #First we will test create campaign api then delete dummy campaign
    def test_create_campaign(self):
        #calling create campaign function
        jsonResponse,response = self.create_campaign()

        # assert conditions checking
        self.assertEqual(response.status_code, 200)
        self.assertIn('campaign_id',jsonResponse)
        self.assertIn('message_id',jsonResponse)
        #deleting campaign
        id = jsonResponse['campaign_id']
        self.delete_campaign(id)



    #Test case for wrong payload for test for test error messsages
    def test_create_campaign_invalid_request(self):
        #invalid payload
        payload = {
            "campaign_name":"test_campaign",
            "campaign_description": "created_campaign_for_testing",
            "status":"Idel",
            "message": "test_message",
            "message_subject": "test_subject",
            "generated_from_recruit":True
        }

        # act
        response = self.app.post('/create_campaign',headers={"Content-Type": "application/json"}, data=payload)
        jsonResponse = self.json_of_response(response)

        # assert
        self.assertEqual(response.status_code, 400)
        self.assertIn('error',jsonResponse)


    #Test case for check payload if not name in payload
    def test_create_campaign_invalid_request_in_not_name(self):
        payload = json.dumps({
            "campaign_description": "created_campaign_for_testing",
            "status": "Idel",
            "message": "test_message",
            "message_subject": "test_subject",
            "generated_from_recruit":True
        })

        # act
        response = self.app.post('/create_campaign',headers={"Content-Type": "application/json"}, data=payload)

        # assert
        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid Request',response.get_data(as_text=True))


    #Test case for get campaign api
    def test_get_campaign(self):

        # act
        response = self.app.get(f'/create_campaign')
        jsonResponses = self.json_of_response(response)
        
        # checking assert conditions
        self.assertEqual(response.status_code, 200)
        for jsonResponse in jsonResponses:
            self.assertEqual(dict,type(jsonResponse))
            self.assertGreater(len(jsonResponse),0)
            self.assertIn('Campaign_name', jsonResponse)
            self.assertIn('creation_date', jsonResponse)
            self.assertIn('Campaign_description', jsonResponse)
            self.assertIn('status', jsonResponse)
            self.assertIn('generated_from_recruit', jsonResponse)
            self.assertIn('message_detail', jsonResponse)


    #Test delete campaign api
    def test_delete_campaign(self):
        #calling create campaign function
        jsonResponse,response = self.create_campaign()
        id = jsonResponse['campaign_id']

        # testing delete campaign api 
        response = self.app.delete(f'/delete_campaign/'+id)

        # assert conditions checking
        self.assertEqual(response.status_code, 200)
        self.assertIn("Campaign deleted",response.get_data(as_text=True))
        

    #Test cases for pause campaign api
    def test_pause_campaign(self):
        #calling function for create a dummy campaign
        jsonResponse,response = self.create_campaign()
        id = jsonResponse['campaign_id']
        #hardcoded value for pause campaign
        status = "0"
        # testing pause campaign api
        response = self.app.post('/pause_campaign/'+id+'/'+status)

        # assert conditons checking
        self.assertEqual(response.status_code, 200)
        self.delete_campaign(id)


    #Testing list campaign api 
    def test_list_campaign(self):
        # act
        response = self.app.get(f'/list_campaign')
        jsonResponses = self.json_of_response(response)
        # assert
        self.assertEqual(response.status_code, 200)
        for jsonResponse in jsonResponses:
            self.assertEqual(dict,type(jsonResponse))
            self.assertGreater(len(jsonResponse),0)
            self.assertIn('Campaign_name', jsonResponse)
            self.assertIn('creation_date', jsonResponse)
            self.assertIn('Campaign_description', jsonResponse)
            self.assertIn('status', jsonResponse)
            self.assertIn('generated_from_recruit', jsonResponse)
            self.assertIn('message_detail', jsonResponse)


