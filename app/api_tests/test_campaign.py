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


    #Test delete campaign api
    def test_user_delete_campaign(self):
        #calling create campaign function
        campaign_id = "5ef48f8619b4326a7ece8c8f"
        user_id = "5ef48fc019b4326a7ece8c91"
        # testing delete campaign api 
        response = self.app.delete(f'/user_delete_campaign/'+campaign_id+'/'+user_id)

        # assert conditions checking
        self.assertEqual(response.status_code, 200)
        self.assertIn("User deleted from campaign",response.get_data(as_text=True))


    #Test campaign details api
    def test_campaign_deatils(self):
        #calling campaign details function
        campaign_id = "5ef48f8619b4326a7ece8c8f"
        # testing campaign details api 
        response = self.app.get(f'/campaign_detail/'+campaign_id)
        jsonResponses = self.json_of_response(response)
    
        # assert conditions checking
        self.assertEqual(response.status_code, 200)
        self.assertIn("Campaign_description",jsonResponses)
        self.assertIn("Campaign_name",jsonResponses)
        self.assertIn("_id",jsonResponses)
        self.assertIn("clicking_details",jsonResponses)
        self.assertIn("creation_date",jsonResponses)
        self.assertIn("delay",jsonResponses)
        self.assertIn("message_detail",jsonResponses)
        self.assertIn("smtps",jsonResponses)
        self.assertIn("status",jsonResponses)
        self.assertIn("users",jsonResponses)
        self.assertIn("total_expected_time_of_completion",jsonResponses)
        self.assertIn("unsubscribed_users",jsonResponses)
        self.assertIn("seen_rate",jsonResponses)
        self.assertIn("open_rate",jsonResponses)
        self.assertIn("generated_from_recruit",jsonResponses)
        self.assertIn("bounce_rate",jsonResponses)


    #Test campaign details api
    def test_mails_status(self):
        skip = "0"
        limit = "100"
        # testing campaign details api 
        response = self.app.get(f'/mails_status?skip='+skip+'&'+'limit='+limit)
        jsonResponse = self.json_of_response(response)
            
        # assert conditions checking
        self.assertEqual(response.status_code, 200)
        for jsonResponses in jsonResponse:
            self.assertIn("_id",jsonResponses)
            self.assertIn("bounce",jsonResponses)
            self.assertIn("bounce_type",jsonResponses)
            self.assertIn("campaign",jsonResponses)
            self.assertIn("clicked",jsonResponses)
            self.assertIn("digit",jsonResponses)
            self.assertIn("mail_sended_status",jsonResponses)
            self.assertIn("message",jsonResponses)
            self.assertIn("recipients",jsonResponses)
            self.assertIn("seen",jsonResponses)
            self.assertIn("sending_mail",jsonResponses)
            self.assertIn("sending_password",jsonResponses)
            self.assertIn("sending_port",jsonResponses)
            self.assertIn("sending_server",jsonResponses)
            self.assertIn("sending_time",jsonResponses)
            self.assertIn("user_mail",jsonResponses)
            

    #Test unsubscriber status api
    def test_unsubscribers_status(self):
        skip = "0"
        limit = "100"
        # testing campaign details api 
        response = self.app.get(f'/unsub_status?skip='+skip+'&'+'limit='+limit)
        jsonResponse = self.json_of_response(response)
            
        # assert conditions checking
        self.assertEqual(response.status_code, 200)
        self.assertIn("list",jsonResponse)
        self.assertIn("totalUnsub",jsonResponse)



    #Test unsubscriber status api
    def test_unsubscribe_user(self):
        Id = "5ea80fc4ea89f8d6cade3976"
        # testing campaign details api 
        response = self.app.get(f'/delete_unsub_status/'+Id)
            
        # assert conditions checking
        self.assertEqual(response.status_code, 200)
        self.assertIn("user removed from unsub",response.get_data(as_text=True))


    def test_edit_template(self):
        payload = json.dumps({
            "message": "created_campaign_for_testing",
            "message_key": "Idel",
            "message_origin": "test_message",
            "message_subject": "test_subject",
            "recruit_details":True
        })
        template_id = "5dea40490356855a0b3200a7"
        # act
        response = self.app.post('edit_templates/'+template_id,headers={"Content-Type": "application/json"}, data=payload)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Template Updated",response.get_data(as_text=True))


    #Test daily_validate status api
    def test_daily_validate_details(self):
        skip = "0"
        limit = "100"
        # testing campaign details api 
        response = self.app.get(f'/daily_validate_details?skip='+skip+'&'+'limit='+limit)
        jsonResponse = self.json_of_response(response)
        # assert conditions checking
        self.assertEqual(response.status_code, 200)
        for jsonResponses in jsonResponse:
            self.assertIn("_id",jsonResponses)
            self.assertIn("count",jsonResponses)
            self.assertIn("created_at",jsonResponses)
            self.assertIn("email",jsonResponses)
            self.assertIn("smtp",jsonResponses)

    #test campaign_smtp_test
    def test_campaign_smtp_test(self):
        payload = json.dumps({
            "email":"aayush_saini@excellencetechnologies.in",
            "message":"testing message",
            "message_subject":"testing"
            })

        # act
        response = self.app.post('/campaign_smtp_test',headers={"Content-Type": "application/json"}, data=payload)

        #assert
        self.assertEqual(response.status_code, 200)
        self.assertIn("sended",response.get_data(as_text=True))
