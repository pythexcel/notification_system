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




    def create_mail_template(self):
        payload = {
                "Doc_type" : "email",
                "for" : "when interview first round mail is sent",
                "message" : "Hi,#name: <br/> Your First round with #company: has been schedule on #date: at the #venue: for #job_profile: <br/> #hr_signature: ",
                "message_key" : "first_round",
                "message_origin" : "RECRUIT",
                "message_subject" : "#name!,your interview for First round of #job_profile: is scheduled",
                "recruit_details" : "Interview First Round",
                "version" : 1,
                "default" : True,
                "working" : True,
                "mobile_message" : "Hi,#name: Your First round with #company: has been schedule on #date: at the #venue: for #job_profile:"
                }
        mongo.db.mail_template.insert_one(payload).inserted_id

    def create_mail_variables(self):
        payload = [{"name" : "#venue","value" : "C-86 B Excellence Technosoft Pvt. Ltd Noida Sector 8","variable_type" : "system"},
                   {"name" : "#map_location","value" : "https://www.google.co.in/maps/place/Excellence+Technologies/@28.5959817,77.3260043,17z/data=!3m1!4b1!4m5!3m4!1s0x390ce4fc8c75d9e:0x4ea29a8e67042fb9!8m2!3d28.595977!4d77.328193?hl=en","variable_type" : "system"},
                   {"name" : "#hr_signature","value" : "<p>HR <br/> Juhi Singh <br/> Landline No: 0120-4113772 <br/> https://excellencetechnologies.in/<br/>https://www.facebook.com/ExcellenceTechnologies<br/>https://itunes.apple.com/in/app/career-app-by-etech/id1399557922?mt=8<br/>","variable_type" : "system"},
                   {"name" : "#company","value" : "Excellence Technosoft Pvt. Ltd","variable_type" : "system"}]
        #data making
        ret = mongo.db.mail_variables.insert_many(payload)
        return ret

    def create_mail_settings(self):
        payload = {"mail_server" : "smtp.gmail.com","mail_port" : 465,"origin" : "RECRUIT","mail_use_tls" : True,"mail_username" : "testnt64@gmail.com","mail_password" : "injbjnzckuqjddgm","active" : True,"type" : "tls","mail_from" : None}
        mongo.db.mail_settings.insert_one(payload).inserted_id


    def test_preview_api(self):
        self.create_mail_template()
        self.create_mail_variables()
        self.create_mail_settings()

        payload = json.dumps({"message_key":"first_round","message":" Hi,#name: <br/> Your First round with Excellence Technosoft Pvt. Ltd has been schedule on #date: at the C-86 B Excellence Technosoft Pvt. Ltd Noida Sector 8 for #job_profile: <br/> <p>HR <br/> Juhi Singh <br/> Landline No: 0120-4113772 <br/> https://excellencetechnologies.in/<br/>https://www.facebook.com/ExcellenceTechnologies<br/>https://itunes.apple.com/in/app/career-app-by-etech/id1399557922?mt=8<br/>  ","subject":"#name!,your interview for First round of #job_profile: is scheduled","to":["aayush_saini@excellencetechnologies.in"],"cc":[],"bcc":[],"smtp_email":"testnt64@gmail.com","phone":None,"phone_message":None,"data":{"name":None}})

        #act
        response = self.app.post('/notify/preview',headers={"Content-Type": "application/json","Secretkey":"gUuWrJauOiLcFSDCL5TM1heITeBVcL"}, data=payload)

        # assert
        self.assertEqual(response.status_code, 200)
        self.assertIn('true',response.get_data(as_text=True))




    #testing send mail test api
    def test_send_mail_api(self):
        payload = json.dumps({
            "message": "This is api test cases testing",
            "subject": "Test cases Testing",
            "to": ["aayush_saini@excellencetechnologies.in"]
        })

        #act
        response = self.app.post('/notify/send_mail',headers={"Content-Type": "application/json","Secretkey":"gUuWrJauOiLcFSDCL5TM1heITeBVcL"}, data=payload)

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
        response = self.app.post('/notify/send_mail',headers={"Content-Type": "application/json","Secretkey":"gUuWrJauOiLcFSDCL5TM1heITeBVcL"}, data=payload)

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
        response = self.app.post('/notify/send_mail',headers={"Content-Type": "application/json","Secretkey":"gUuWrJauOiLcFSDCL5TM1heITeBVcL"}, data=payload)

        # assert
        self.assertEqual(response.status_code, 400)
        self.assertIn('Message subject and recipents not should be none',response.get_data(as_text=True))
    

    #testing get mail settings test api
    def test_smtp_mail_test_api(self):
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
        response = self.app.post('/notify/mail_test',headers={"Content-Type": "application/json","Secretkey":"gUuWrJauOiLcFSDCL5TM1heITeBVcL"}, data=payload)

        # assert
        self.assertEqual(response.status_code, 200)
        self.assertIn('Smtp working',response.get_data(as_text=True))


    #testing mail template requirements test api
    def test_email_template_requirement(self):
        message_key = "Interviwee Hold"

        template_payload = {"Doc_type":"email","default":True,"for":"Interviwee Hold","message":"<p>Dear Applicant<br/>Hope you are doing good!<br/>This is to inform you that with respect your application and subsequent interview with #company: your candidature has been put on hold for a while due to unavoidable circumstance.<br/>We will surely get back to you once the position re-opens. Thank you so much for showing your pleasant interest with the company and the job.<br/>Regards<br/> #hr_signature: </p>","message_key":"interviewee_onhold","message_origin":"RECRUIT","message_subject":"interviewee put on hold","recruit_details":"Interviewee On Hold","version":1,"working":True}
        mongo.db.mail_template.insert_one(template_payload).inserted_id

        #act
        response = self.app.get('/notify/email_template_requirement/'+message_key,headers={"Secretkey":"gUuWrJauOiLcFSDCL5TM1heITeBVcL"})
        
        #assert
        self.assertEqual(response.status_code, 200)
        self.assertIn('Doc_type',response.get_data(as_text=True))
        self.assertIn('for',response.get_data(as_text=True))
        self.assertIn('message',response.get_data(as_text=True))
        self.assertIn('message_key',response.get_data(as_text=True))
        self.assertIn('message_subject',response.get_data(as_text=True))