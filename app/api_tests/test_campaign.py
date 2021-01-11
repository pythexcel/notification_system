'''
import unittest
from json import dumps
from json.decoder import JSONDecodeError
from requests.exceptions import ConnectionError
import json
from app.api_tests.test_message_create_apis import app
from bson import ObjectId
from app import mongo
import datetime

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

        response = self.app.post('/create_campaign',headers={"Content-Type": "application/json","Secretkey":"gUuWrJauOiLcFSDCL5TM1heITeBVcL"}, data=payload)
        jsonResponse = self.json_of_response(response)
        return jsonResponse,response

    #common function for delete campaign by id
    def delete_campaign(self,id):
        response = self.app.delete(f'/delete_campaign/'+id,headers={"Secretkey":"gUuWrJauOiLcFSDCL5TM1heITeBVcL"})
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
        response = self.app.post('/create_campaign',headers={"Content-Type": "application/json","Secretkey":"gUuWrJauOiLcFSDCL5TM1heITeBVcL"}, data=payload)
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
        response = self.app.post('/create_campaign',headers={"Content-Type": "application/json","Secretkey":"gUuWrJauOiLcFSDCL5TM1heITeBVcL"}, data=payload)

        # assert
        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid Request',response.get_data(as_text=True))


    #Test case for get campaign api
    def test_get_campaign(self):
        payload = {"Campaign_name":"testing","Campaign_description":"test","status":"Completed","generated_from_recruit":False,"message_detail":[{"message_id":"20918026-54e1-497f-8033-770943ac3bb7","message":"testing","message_subject":"testing","count":1}],"bounce_rate":0,"open_rate":0,"seen_rate":0,"unsubscribed_users":0,"delay":3,"smtps":["5eec4fd1796cd69227faa4a0"],"total_expected_time_of_completion":"0.0 second","creation_date":1593085830234}
        id = mongo.db.campaigns.insert_one(payload).inserted_id
        campign_payload = {"name":"aayush","email":"aayush_saini@excellencetechnologies.in","send_status":True,"campaign":str(id),"block":False,"unsubscribe_status":False,"already_unsub":False,"mail_cron":True,"error_message":"SMTPDataError(550, b'5.4.5 Daily user sending quota exceeded. v4sm16752194wro.26 - gsmtp')","error_time":1593105790535,"successful":True,"mail_message":[{"sended_message_details":"5c1cbb41-361f-441e-a365-44179fd673da","campaign":str(id)}],"sended_date":1593569827965}
        idd = mongo.db.campaign_users.insert_one(campign_payload).inserted_id
        template_payload = {"Doc_type":"email","for":"Interviwee Hold","message":"<p>Dear Applicant<br/>Hope you are doing good!<br/>This is to inform you that with respect your application and subsequent interview with #company: your candidature has been put on hold for a while due to unavoidable circumstance.<br/>We will surely get back to you once the position re-opens. Thank you so much for showing your pleasant interest with the company and the job.<br/>Regards<br/> #hr_signature: </p>","message_key":"interviewee_onhold","message_origin":"RECRUIT","message_subject":"interviewee put on hold","recruit_details":"Interviewee On Hold","version":1,"working":True,"template_head":str(idd)}
        mongo.db.mail_template.insert_one(template_payload).inserted_id

        response = self.app.get('/create_campaign',headers={"Secretkey":"gUuWrJauOiLcFSDCL5TM1heITeBVcL"})
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
        response = self.app.delete(f'/delete_campaign/'+id,headers={"Secretkey":"gUuWrJauOiLcFSDCL5TM1heITeBVcL"})

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
        response = self.app.post('/pause_campaign/'+id+'/'+status,headers={"Secretkey":"gUuWrJauOiLcFSDCL5TM1heITeBVcL"})

        # assert conditons checking
        self.assertEqual(response.status_code, 200)
        self.delete_campaign(id)


    #Testing list campaign api 
    def test_list_campaign(self):
        #making data
        jsonResponse,response = self.create_campaign()
        id = jsonResponse['campaign_id']
        campign_payload = {"name":"aayush","email":"aayush_saini@excellencetechnologies.in","send_status":True,"campaign":str(id),"block":False,"unsubscribe_status":False,"already_unsub":False,"mail_cron":True,"error_message":"SMTPDataError(550, b'5.4.5 Daily user sending quota exceeded. v4sm16752194wro.26 - gsmtp')","error_time":1593105790535,"successful":True,"mail_message":[{"sended_message_details":"5c1cbb41-361f-441e-a365-44179fd673da","campaign":str(id)}],"sended_date":1593569827965}
        idd = mongo.db.campaign_users.insert_one(campign_payload).inserted_id
        template_payload = {"Doc_type":"email","for":"Interviwee Hold","message":"<p>Dear Applicant<br/>Hope you are doing good!<br/>This is to inform you that with respect your application and subsequent interview with #company: your candidature has been put on hold for a while due to unavoidable circumstance.<br/>We will surely get back to you once the position re-opens. Thank you so much for showing your pleasant interest with the company and the job.<br/>Regards<br/> #hr_signature: </p>","message_key":"interviewee_onhold","message_origin":"RECRUIT","message_subject":"interviewee put on hold","recruit_details":"Interviewee On Hold","version":1,"working":True,"template_head":str(idd)}
        mongo.db.mail_template.insert_one(template_payload).inserted_id

        # act
        response = self.app.get(f'/list_campaign',headers={"Secretkey":"gUuWrJauOiLcFSDCL5TM1heITeBVcL"})
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
        #making data
        jsonResponse,response = self.create_campaign()
        id = jsonResponse['campaign_id']

        campign_payload = {"name":"aayush","email":"aayush_saini@excellencetechnologies.in","send_status":True,"campaign":str(id),"block":False,"unsubscribe_status":False,"already_unsub":False,"mail_cron":True,"error_message":"SMTPDataError(550, b'5.4.5 Daily user sending quota exceeded. v4sm16752194wro.26 - gsmtp')","error_time":1593105790535,"successful":True,"mail_message":[{"sended_message_details":"5c1cbb41-361f-441e-a365-44179fd673da","campaign":str(id)}],"sended_date":1593569827965}
        user_id = mongo.db.campaign_users.insert_one(campign_payload).inserted_id

        # testing delete campaign api 
        response = self.app.delete(f'/user_delete_campaign/'+str(id)+'/'+str(user_id),headers={"Secretkey":"gUuWrJauOiLcFSDCL5TM1heITeBVcL"})

        # assert conditions checking
        self.assertEqual(response.status_code, 200)
        self.assertIn("User deleted from campaign",response.get_data(as_text=True))


    #Test campaign details api
    def test_campaign_deatils(self):
        #calling campaign details function
        jsonResponse,response = self.create_campaign()
        campaign_id = jsonResponse['campaign_id'] 

        # testing campaign details api 
        response = self.app.get(f'/campaign_detail/'+campaign_id,headers={"Secretkey":"gUuWrJauOiLcFSDCL5TM1heITeBVcL"})
        jsonResponses = self.json_of_response(response)
    
        # assert conditions checking
        self.assertEqual(response.status_code, 200)
        self.assertIn("Campaign_description",jsonResponses)
        self.assertIn("Campaign_name",jsonResponses)
        self.assertIn("_id",jsonResponses)
        self.assertIn("clicking_details",jsonResponses)
        self.assertIn("creation_date",jsonResponses)
        self.assertIn("message_detail",jsonResponses)
        self.assertIn("status",jsonResponses)
        self.assertIn("users",jsonResponses)
        self.assertIn("generated_from_recruit",jsonResponses)


    #Test campaign details api
    def test_mails_status(self):
        #making data
        payload = {"user_mail":"aayush_saini@excellencetechnologies.in","user_id":"5ef48fa719b4326a7ece8c90","message":"testing","mail_sended_status":True,"subject":"testing","recipients":["aayush_saini@excellencetechnologies.in"],"digit":"5c1cbb41-361f-441e-a365-44179fd673da","campaign":"5ef48f8619b4326a7ece8c8f","sending_mail":"roggermanning08@gmail.com","sending_password":"guapagzobitpiskm","sending_server":"smtp.gmail.com","seen":False,"sending_port":465,"clicked":False,"bounce_type":"pending","bounce":False}
        mongo.db.mail_status.insert_one(payload)
        skip = "0"
        limit = "100"
        # testing campaign details api 
        response = self.app.get(f'/mails_status?skip='+skip+'&'+'limit='+limit,headers={"Secretkey":"gUuWrJauOiLcFSDCL5TM1heITeBVcL"})
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
            self.assertIn("user_mail",jsonResponses)
            

    #Test unsubscriber status api
    def test_unsubscribers_status(self):
        payload = {"user":"rogger","email":"roger@gmail.com","unsubscribe_at":datetime.datetime.now()}
        skip = "0"
        limit = "100"
        mongo.db.unsubscribed_users.insert_one(payload).inserted_id
        # testing campaign details api 
        response = self.app.get(f'/unsub_status?skip='+skip+'&'+'limit='+limit,headers={"Secretkey":"gUuWrJauOiLcFSDCL5TM1heITeBVcL"})
        jsonResponse = self.json_of_response(response)
            
        # assert conditions checking
        self.assertEqual(response.status_code, 200)
        self.assertIn("list",jsonResponse)
        self.assertIn("totalUnsub",jsonResponse)



    #Test unsubscriber status api
    def test_unsubscribe_user(self):
        payload = {"user":"rogger","email":"roger@gmail.com","unsubscribe_at":datetime.datetime.now()}
        Id = mongo.db.unsubscribed_users.insert_one(payload).inserted_id
        # testing campaign details api 
        response = self.app.get(f'/delete_unsub_status/'+str(Id),headers={"Secretkey":"gUuWrJauOiLcFSDCL5TM1heITeBVcL"})
            
        # assert conditions checking
        self.assertEqual(response.status_code, 200)
        self.assertIn("user removed from unsub",response.get_data(as_text=True))


    def test_edit_template(self):
        template_payload = {
            "message": "created_campaign_for_testing",
            "message_key": "Idel",
            "message_origin": "test_message",
            "message_subject": "test_subject",
            "recruit_details":True
        }
        template_id = mongo.db.mail_template.insert_one(template_payload).inserted_id
        payload = json.dumps({
            "message": "created_campaign_for_testing",
            "message_key": "Idel",
            "message_origin": "updated origin",
            "message_subject": "test_subject",
            "recruit_details":True
        })


        # act
        response = self.app.post('edit_templates/'+str(template_id),headers={"Content-Type": "application/json","Secretkey":"gUuWrJauOiLcFSDCL5TM1heITeBVcL"}, data=payload)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Template Updated",response.get_data(as_text=True))


    #Test daily_validate status api
    def test_daily_validate_details(self):
        payload = {"smtp":"smtp.gmail.com","email":"roggermanning08@gmail.com","created_at":1592566731968,"count":11}
        mongo.db.smtp_count_validate.insert_one(payload).inserted_id
        skip = "0"
        limit = "100"
        # testing campaign details api 
        response = self.app.get(f'/daily_validate_details?skip='+skip+'&'+'limit='+limit,headers={"Secretkey":"gUuWrJauOiLcFSDCL5TM1heITeBVcL"})
        jsonResponse = self.json_of_response(response)
        # assert conditions checking
        self.assertEqual(response.status_code, 200)
        for jsonResponses in jsonResponse:
            self.assertIn("_id",jsonResponses)
            self.assertIn("count",jsonResponses)
            self.assertIn("created_at",jsonResponses)
            self.assertIn("email",jsonResponses)
            self.assertIn("smtp",jsonResponses)

    """
    #test campaign_smtp_test
    def test_campaign_smtp_test(self):
        mail_setting_payload = {"mail_server":"smtp.gmail.com","mail_port":465,"origin":"CAMPAIGN","mail_use_tls":True,"mail_username":"etechmusic8@gmail.com","mail_password":"dwxdfpovcucnqcms","active":True,"type":"tls","daemon_mail":"mailer-daemon@googlemail.com","priority":3,"mail_from":None,"created_at":datetime.datetime.now()}
        mongo.db.mail_settings.insert_one(mail_setting_payload).inserted_id
        payload = json.dumps({
            "email":"aayush_saini@excellencetechnologies.in",
            "message":"testing message",
            "message_subject":"testing"
            })

        # act
        response = self.app.post('/campaign_smtp_test',headers={"Content-Type": "application/json","Secretkey":"gUuWrJauOiLcFSDCL5TM1heITeBVcL"}, data=payload)

        #assert
        self.assertEqual(response.status_code, 200)
        self.assertIn("sended",response.get_data(as_text=True))
    """
'''