import unittest
from json import dumps
from json.decoder import JSONDecodeError
from requests.exceptions import ConnectionError
import json
from app.api_tests.test_message_create_apis import app
from bson import ObjectId
import datetime
from app import mongo

class AllTestMailsettingApis(unittest.TestCase):

    def setUp(self):
        app.testing = True
        self.app = app.test_client()

    def tearDown(self):
        pass

    def json_of_response(self, response):
        return json.loads(response.data.decode('utf8'))

"""
    def create_mail_variables(self):
        payload = [{"name":"#employee_name","value":None,"variable_type":"system"},
                   {"name":"#date","value":None,"variable_type":"system"},
                   {"name":"#joining_date","value":None,"variable_type":"system"},
                   {"name":"#logo","value":"<img src='Excelogo-black.jpg' style='max-height:30px'>","variable_type":"system"},
                   {"name":"#employee_email_id","value":None,"variable_type":"system"},
                   {"name":"#director_signature","value":"<p><strong>Excellence Technologies,</strong></p>\n<p><strong>Manish Prakash</strong></p>\n<p><strong>(Director)</strong></p>","variable_type":"user"},
                   {"name":"#venue","value":"C-86 B Excellence Technosoft Pvt. Ltd Noida Sector 8","variable_type":"system"},
                   {"name":"#hr_signature","value":"<p>HR <br/> Juhi Singh <br/> Landline No: 0120-4113772 <br/> https://excellencetechnologies.in/<br/>https://www.facebook.com/ExcellenceTechnologies<br/>https://itunes.apple.com/in/app/career-app-by-etech/id1399557922?mt=8<br/>","variable_type":"system"}]

        #data making
        ret = mongo.db.mail_variables.insert_many(payload)
        return ret


    #testing send mail test api
    def test_send_mail_api(self):
        payload = json.dumps({
            "message": "This is api test cases testing",
            "subject": "Test cases Testing",
            "to": ["aayush_saini@excellencetechnologies.in"]
        })

        #act
        response = self.app.post('/notify/send_mail',headers={"Content-Type": "application/json"}, data=payload)

        # assert
        self.assertEqual(response.status_code, 200)
        self.assertIn('Sended',response.get_data(as_text=True))


    #testing send mail api
    def test_send_mail_api_to_not_available(self):
        payload = json.dumps({
            "message": "This is api test cases testing",
            "subject": "Test cases Testing"
        })

        #act
        response = self.app.post('/notify/send_mail',headers={"Content-Type": "application/json"}, data=payload)

        # assert
        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid Request',response.get_data(as_text=True))


    #testing send mail api if message not available
    def test_send_mail_api_message_not_available(self):
        payload = json.dumps({
            "subject": "Test cases Testing",
            "to":["aayush_saini@excellencetechnologies.in"]
        })

        #act
        response = self.app.post('/notify/send_mail',headers={"Content-Type": "application/json"}, data=payload)

        # assert
        self.assertEqual(response.status_code, 400)
        self.assertIn('Message subject and recipents not should be none',response.get_data(as_text=True))
    

    #testing get mail settings test api
    def test_get_mail_settings(self):
        mail_setting = {"mail_server":"smtp.gmail.com","mail_port":465,"origin":"CAMPAIGN","mail_use_tls":True,"mail_username":"etechmusic8@gmail.com","mail_password":"dwxdfpovcucnqcms","active":True,"type":"tls","daemon_mail":"mailer-daemon@googlemail.com","priority":3,"mail_from":None,"created_at":datetime.datetime.now()}
        mongo.db.mail_settings.insert_one(mail_setting).inserted_id
        self.create_mail_variables()
        letterpayload = {
            "name": "test_letter_head",
            "header_value": '<p> <div id="header"> <div style="height: 5px; background-color: #4bb698;">&nbsp;</div> <div style="height: 8px; margin-top: 1px; background-color: #4bb698;">&nbsp;</div> <div style="height: 5px; margin-top: 1px; background-color: #4bb698;">&nbsp;</div> <br /> <div style="text-align: right; padding-right:40px"><img src="https://res.cloudinary.com/dp0y84e66/image/upload/v1568791251/logo.e5be347d_yf4q90.png" style="width: 150px;" /></div> </div>',
            "footer_value": '<div id="footer" style="bottom: 0; position: absolute; width: 100%;"><hr /> <div>ExcellenceTechnosoft Pvt Ltd</div> <div>CIN: U72200DL2010PTC205087</div> <div>Corp Office:C84-A, Sector 8,Noida, U.P. - 201301</div> <div>Regd Office: 328 GAGAN VIHAR IST MEZZAZINE,NEW DELHI-110051</div> <div style="height: 5px; margin-top: 5px; margin-bottom: 2px; background-color: #4bb698;">&nbsp;</div> </div>',
            "working": True
        }
        id = mongo.db.letter_heads.insert_one(letterpayload).inserted_id

        payload = json.dumps({
            "email": "testnt64@gmail.com"
        })

        #act
        response = self.app.post('/notify/mail_test',headers={"Content-Type": "application/json"}, data=payload)

        # assert
        self.assertEqual(response.status_code, 200)
        self.assertIn('Smtp working',response.get_data(as_text=True))


    #testing mail template requirements test api
    def test_email_template_requirement(self):
        message_key = "first_round"

        template_payload = {"Doc_type":"email","for":"Interviwee Hold","message":"<p>Dear Applicant<br/>Hope you are doing good!<br/>This is to inform you that with respect your application and subsequent interview with #company: your candidature has been put on hold for a while due to unavoidable circumstance.<br/>We will surely get back to you once the position re-opens. Thank you so much for showing your pleasant interest with the company and the job.<br/>Regards<br/> #hr_signature: </p>","message_key":"interviewee_onhold","message_origin":"RECRUIT","message_subject":"interviewee put on hold","recruit_details":"Interviewee On Hold","version":1,"working":True,"template_head":str(idd)}
        mongo.db.mail_template.insert_one(template_payload).inserted_id

        #act
        response = self.app.get('/notify/email_template_requirement/'+message_key)
        #assert
        self.assertEqual(response.status_code, 200)
"""