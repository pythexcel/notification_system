
import unittest
from json import dumps
from json.decoder import JSONDecodeError
from requests.exceptions import ConnectionError
import json
from app import create_app
from bson import ObjectId
from app import mongo
from app.config import account_name,secret_key
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
    
    #testing for special variables api
    def test_special_variables(self):
        #making data
        self.create_mail_variables()
        # act
        response = self.app.get('/message/special_variable?account-name='+account_name,headers={"Secretkey":str(secret_key)})
        jsonResponse = self.json_of_response(response)
        # assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list,type(jsonResponse))
        self.assertGreater(len(jsonResponse),0)
        for jsonRespons in jsonResponse:
            self.assertIn('_id', jsonRespons)
            self.assertIn('name', jsonRespons)
            self.assertIn('value', jsonRespons)
            self.assertIn('variable_type', jsonRespons)
        
    
    #Tesing for put special variable api
    def test_put_special_variables(self):
        payload = json.dumps({
            "name": "test_name",
            "value": "test_value",
            "variable_type": "test_variable_type"
        })

        # act
        response = self.app.put('/message/special_variable?account-name='+account_name,headers={"Content-Type": "application/json","Secretkey":str(secret_key)}, data=payload)

        # assert
        self.assertEqual(response.status_code, 200)
        self.assertIn('upsert',response.get_data(as_text=True))

    
    #Testing get notification api
    def test_get_notification_message(self):
        #making data
        payload = [{"message_key":"weekly_reviewed_notification","channels":"public","email_group":None,"for_email":False,"for_phone":False,"for_slack":True,"message":"@user: your weekly report is reviewed by @manager: with @rating: rating and @comment: .","message_color":"#764FA5","message_origin":"TMS","message_type":"simple_message","sended_to":"private","slack_channel":[""],"working":True},
                   {"message_key":"weekly_notification","channels":"private","email_group":None,"for_email":False,"for_phone":False,"for_slack":True,"message":"@user: your junior @junior: created weekly report.you can review report with below ratings or review manually.\n Report: \n @report: \n Extra: \n @extra: ","message_color":None,"message_origin":"TMS","message_type":"simple_message","sended_to":"private","slack_channel":None,"working":True,"submission_type":None},
                   {"message_key":"expire_weekly_notification","channels":"public","email_group":None,"for_email":False,"for_phone":False,"for_slack":True,"message":"Hi @user: this is regenerated link. Previous link was expired. You can review your @junior: report now \n Report: \n @report: \n Extra: \n @extra:","message_color":None,"message_origin":"TMS","message_type":"simple_message","sended_to":"private","slack_channel":None,"working":True,"submission_type":None}]
        mongo.db.notification_msg.insert_many(payload)
        message_origin = "TMS"
        
        # act
        response = self.app.get(f'/message/configuration/'+message_origin+'?account-name='+account_name,headers={"Secretkey":str(secret_key)})
        jsonResponse = self.json_of_response(response)

        # assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list,type(jsonResponse))
        self.assertGreater(len(jsonResponse),0)
        for jsonRespons in jsonResponse:
            self.assertIn('message', jsonRespons)
            self.assertIn('message_key', jsonRespons)
            self.assertIn('message_origin', jsonRespons)
            self.assertIn('message_type', jsonRespons)
            self.assertIn('sended_to', jsonRespons)
            self.assertIn('slack_channel', jsonRespons)


    
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
        response = self.app.put(f'/message/configuration/'+message_origin+'?account-name='+account_name,headers={"Content-Type": "application/json","Secretkey":str(secret_key)}, data=payload)
        
        # assert
        self.assertEqual(response.status_code, 200)
        self.assertIn('upsert',response.get_data(as_text=True))

    
    #Testing get email tempalate api
    def test_get_email_template(self):
        #making data
        payload = {"Doc_type":"email","for":"Interviwee Hold","message":"<p>Dear Applicant<br/>Hope you are doing good!<br/>This is to inform you that with respect your application and subsequent interview with #company: your candidature has been put on hold for a while due to unavoidable circumstance.<br/>We will surely get back to you once the position re-opens. Thank you so much for showing your pleasant interest with the company and the job.<br/>Regards<br/> #hr_signature: </p>","message_key":"interviewee_onhold","message_origin":"RECRUIT","message_subject":"interviewee put on hold","recruit_details":"Interviewee On Hold","version":1,"working":True,"template_head":"5f0c16db3fbe9cf9946700df"}
        mongo.db.mail_template.insert_one(payload)

        #making data
        self.create_mail_variables()

        payload = {"name":"test_letter_head","footer_value":"<div id=\"footer\" style=\"bottom: 0; position: absolute; width: 100%;\"><hr /> <div>ExcellenceTechnosoft Pvt Ltd</div> <div>CIN: U72200DL2010PTC205087</div> <div>Corp Office:C84-A, Sector 8,Noida, U.P. - 201301</div> <div>Regd Office: 328 GAGAN VIHAR IST MEZZAZINE,NEW DELHI-110051</div> <div style=\"height: 5px; margin-top: 5px; margin-bottom: 2px; background-color: #4bb698;\">&nbsp;</div> </div>","header_value":"<p> <div id=\"header\"> <div style=\"height: 5px; background-color: #4bb698;\">&nbsp;</div> <div style=\"height: 8px; margin-top: 1px; background-color: #4bb698;\">&nbsp;</div> <div style=\"height: 5px; margin-top: 1px; background-color: #4bb698;\">&nbsp;</div> <br /> <div style=\"text-align: right; padding-right:40px\"><img src=\"https://res.cloudinary.com/dp0y84e66/image/upload/v1568791251/logo.e5be347d_yf4q90.png\" style=\"width: 150px;\" /></div> </div>","working":True}
        message_origin = "RECRUIT"
        
        # act
        response = self.app.get(f'/message/get_email_template/'+message_origin+'?account-name='+account_name,headers={"Secretkey":str(secret_key)})
        jsonResponse = self.json_of_response(response)

        # assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list,type(jsonResponse))
        self.assertGreater(len(jsonResponse),0)
        for jsonRespons in jsonResponse:
            self.assertIn('Doc_type', jsonRespons)
            self.assertIn('for', jsonRespons)
            self.assertIn('message', jsonRespons)
            self.assertIn('message_key', jsonRespons)
            self.assertIn('message_origin', jsonRespons)
            self.assertIn('message_subject', jsonRespons)
            self.assertIn('recruit_details', jsonRespons)
            self.assertIn('template_variables', jsonRespons)
            self.assertIn('working', jsonRespons)

    
    #testing delete email template apis
    def test_delete_email_template(self):
        #making data
        payload = {"Doc_type":"email","for":"Interviwee Hold","message":"<p>Dear Applicant<br/>Hope you are doing good!<br/>This is to inform you that with respect your application and subsequent interview with #company: your candidature has been put on hold for a while due to unavoidable circumstance.<br/>We will surely get back to you once the position re-opens. Thank you so much for showing your pleasant interest with the company and the job.<br/>Regards<br/> #hr_signature: </p>","message_key":"interviewee_onhold","message_origin":"RECRUIT","message_subject":"interviewee put on hold","recruit_details":"Interviewee On Hold","version":1,"working":True,"template_head":"5f0c16db3fbe9cf9946700df"}
        mongo.db.mail_template.insert_one(payload)

        message_origin = "RECRUIT"
        payload = json.dumps({
            "message_key": "interviewee_onhold"
        })
        
        # act
        response = self.app.post(f'/message/get_email_template/'+message_origin+'?account-name='+account_name,headers={"Content-Type": "application/json","Secretkey":str(secret_key)}, data=payload)

        # assert
        self.assertEqual(response.status_code, 200)
        self.assertIn("Template Deleted",response.get_data(as_text=True))

    
    #testing delete attachment api
    def test_delete_attachment_file(self):
        #making data
        payload = {"Doc_type":"email","attachment_file":None,"attachment_file_name":None,"for":None,"message":"<p><br></p><p>Dear <strong>#name:,</strong></p><p>Welcome to #company:</p><p><br>Some of the company policy documents are attached with this mail. Before you start working in the office, kindly go through to all of them and get a clear understanding of company policies, work culture and environment.</p><p>Once you are well versed with them, you can proceed with your work. In case of any doubt feel free to contact.<br>#hr_signature:<br>#logo:</p>","message_key":"Important HR guidelines and Company Policies","message_origin":"HR","message_subject":"Important Information - #company:","version":5,"working":True,"default":False,"version_details":[{"message":"<p><br></p><p>Dear <strong>#name:,</strong></p><p>Welcome to #company:</p><p><br>Some of the company policy documents are attached with this mail. Before you start working in the office, kindly go through to all of them and get a clear understanding of company policies, work culture and environment.</p><p>Once you are well versed with them, you can proceed with your work. In case of any doubt feel free to contact.<br>#hr_signature:<br>#logo:</p>","version":1},{"message":"<p><br></p><p>Dear <strong>#name:,</strong></p><p>Welcome to #company:</p><p><br>Some of the company policy documents are attached with this mail. Before you start working in the office, kindly go through to all of them and get a clear understanding of company policies, work culture and environment.</p><p>Once you are well versed with them, you can proceed with your work. In case of any doubt feel free to contact.<br>#hr_signature:<br>#logo:</p>","version":2},{"message":"<p><br></p><p>Dear <strong>#name:,</strong></p><p>Welcome to #company:</p><p><br>Some of the company policy documents are attached with this mail. Before you start working in the office, kindly go through to all of them and get a clear understanding of company policies, work culture and environment.</p><p>Once you are well versed with them, you can proceed with your work. In case of any doubt feel free to contact.<br>#hr_signature:<br>#logo:</p>","version":3},{"message":"<p><br></p><p>Dear <strong>#name:,</strong></p><p>Welcome to #company:</p><p><br>Some of the company policy documents are attached with this mail. Before you start working in the office, kindly go through to all of them and get a clear understanding of company policies, work culture and environment.</p><p>Once you are well versed with them, you can proceed with your work. In case of any doubt feel free to contact.<br>#hr_signature:<br>#logo:</p>","version":4}],"recruit_details":None,"attachment_files":[{"file_id":"72d741fb-f568-4659-b6c1-80f8af2e0e4f","file_name":"block2_3.png","file":"/home/python/projects/notification_system/attached_documents/block2_3.png"},{"file_id":"c4a46a1d-11d6-4a36-a3f9-8984c6e3f4b2","file_name":"block2_4.png","file":"/home/python/projects/notification_system/attached_documents/block2_4.png"},{"file_id":"20cc5ef1-89ac-4392-a3e9-fb1b757fce57","file_name":"block2_3.png","file":"/home/python/projects/notification_system/attached_documents/block2_3.png"},{"file_id":"9d10b8ee-2b3d-4449-a1ab-d1a61bbff8dd","file_name":"block2_1.png","file":"/home/python/projects/notification_system/attached_documents/block2_1.png"}]}
        id = mongo.db.mail_template.insert_one(payload).inserted_id
        file_id = "9d10b8ee-2b3d-4449-a1ab-d1a61bbff8dd"

        # act
        response = self.app.delete(f'/message/delete_file/'+str(id)+'/'+file_id+'?account-name='+account_name,headers={"Secretkey":str(secret_key)})

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
        response = self.app.put(f'/message/letter_heads?account-name='+account_name,headers={"Content-Type": "application/json","Secretkey":str(secret_key)}, data=payload)
        
        # assert
        self.assertEqual(response.status_code, 200)
        self.assertIn("Letter Head Created",response.get_data(as_text=True))

    
    #testing get letter head api
    def test_get_letter_head(self):
        #making data
        self.test_put_letter_head()

        # act
        response = self.app.get(f'/message/letter_heads?account-name='+account_name,headers={"Secretkey":str(secret_key)})
        jsonResponse = self.json_of_response(response)

        # assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list,type(jsonResponse))
        self.assertGreater(len(jsonResponse),0)
        for jsonRespons in jsonResponse:
            self.assertIn('footer_value', jsonRespons)
            self.assertIn('header_value', jsonRespons)
            self.assertIn('name', jsonRespons)
            self.assertIn('working', jsonRespons)

    
    #test case for delete letter head api
    def test_delete_letter_head(self):
        payload = {
            "name": "test_letter_head",
            "header_value": '<p> <div id="header"> <div style="height: 5px; background-color: #4bb698;">&nbsp;</div> <div style="height: 8px; margin-top: 1px; background-color: #4bb698;">&nbsp;</div> <div style="height: 5px; margin-top: 1px; background-color: #4bb698;">&nbsp;</div> <br /> <div style="text-align: right; padding-right:40px"><img src="https://res.cloudinary.com/dp0y84e66/image/upload/v1568791251/logo.e5be347d_yf4q90.png" style="width: 150px;" /></div> </div>',
            "footer_value": '<div id="footer" style="bottom: 0; position: absolute; width: 100%;"><hr /> <div>ExcellenceTechnosoft Pvt Ltd</div> <div>CIN: U72200DL2010PTC205087</div> <div>Corp Office:C84-A, Sector 8,Noida, U.P. - 201301</div> <div>Regd Office: 328 GAGAN VIHAR IST MEZZAZINE,NEW DELHI-110051</div> <div style="height: 5px; margin-top: 5px; margin-bottom: 2px; background-color: #4bb698;">&nbsp;</div> </div>',
            "working": True
        }
        id = mongo.db.letter_heads.insert_one(payload).inserted_id

        response = self.app.delete(f'/message/letter_heads/'+str(id)+'?account-name='+account_name,headers={"Secretkey":str(secret_key)})

        # assert
        self.assertEqual(response.status_code, 200)
        self.assertIn("Letter Head Deleted",response.get_data(as_text=True))

    
    #test case for assign letter head api
    def test_assign_letter_head(self):
        #making data
        payload = {"Doc_type":"email","attachment_file":None,"attachment_file_name":None,"for":None,"message":"<p><br></p><p>Dear <strong>#name:,</strong></p><p>Welcome to #company:</p><p><br>Some of the company policy documents are attached with this mail. Before you start working in the office, kindly go through to all of them and get a clear understanding of company policies, work culture and environment.</p><p>Once you are well versed with them, you can proceed with your work. In case of any doubt feel free to contact.<br>#hr_signature:<br>#logo:</p>","message_key":"Important HR guidelines and Company Policies","message_origin":"HR","message_subject":"Important Information - #company:","version":5,"working":True,"default":False,"version_details":[{"message":"<p><br></p><p>Dear <strong>#name:,</strong></p><p>Welcome to #company:</p><p><br>Some of the company policy documents are attached with this mail. Before you start working in the office, kindly go through to all of them and get a clear understanding of company policies, work culture and environment.</p><p>Once you are well versed with them, you can proceed with your work. In case of any doubt feel free to contact.<br>#hr_signature:<br>#logo:</p>","version":1},{"message":"<p><br></p><p>Dear <strong>#name:,</strong></p><p>Welcome to #company:</p><p><br>Some of the company policy documents are attached with this mail. Before you start working in the office, kindly go through to all of them and get a clear understanding of company policies, work culture and environment.</p><p>Once you are well versed with them, you can proceed with your work. In case of any doubt feel free to contact.<br>#hr_signature:<br>#logo:</p>","version":2},{"message":"<p><br></p><p>Dear <strong>#name:,</strong></p><p>Welcome to #company:</p><p><br>Some of the company policy documents are attached with this mail. Before you start working in the office, kindly go through to all of them and get a clear understanding of company policies, work culture and environment.</p><p>Once you are well versed with them, you can proceed with your work. In case of any doubt feel free to contact.<br>#hr_signature:<br>#logo:</p>","version":3},{"message":"<p><br></p><p>Dear <strong>#name:,</strong></p><p>Welcome to #company:</p><p><br>Some of the company policy documents are attached with this mail. Before you start working in the office, kindly go through to all of them and get a clear understanding of company policies, work culture and environment.</p><p>Once you are well versed with them, you can proceed with your work. In case of any doubt feel free to contact.<br>#hr_signature:<br>#logo:</p>","version":4}],"recruit_details":None,"attachment_files":[{"file_id":"72d741fb-f568-4659-b6c1-80f8af2e0e4f","file_name":"block2_3.png","file":"/home/python/projects/notification_system/attached_documents/block2_3.png"},{"file_id":"c4a46a1d-11d6-4a36-a3f9-8984c6e3f4b2","file_name":"block2_4.png","file":"/home/python/projects/notification_system/attached_documents/block2_4.png"},{"file_id":"20cc5ef1-89ac-4392-a3e9-fb1b757fce57","file_name":"block2_3.png","file":"/home/python/projects/notification_system/attached_documents/block2_3.png"},{"file_id":"9d10b8ee-2b3d-4449-a1ab-d1a61bbff8dd","file_name":"block2_1.png","file":"/home/python/projects/notification_system/attached_documents/block2_1.png"}]}
        template_id = mongo.db.mail_template.insert_one(payload).inserted_id

        #payload
        letter_head_id = "5f0c16db3fbe9cf9946700df"

        # act
        response = self.app.put(f'/message/assign_letter_heads/'+str(template_id)+'/'+letter_head_id+'?account-name='+account_name,headers={"Secretkey":str(secret_key)})
        
        # assert
        self.assertEqual(response.status_code, 200)
        self.assertIn("Letter Head Added To Template",response.get_data(as_text=True))

    
    #Test case for trigger api
    def test_get_triggers(self):
        #making data
        payload = {"Doc_type":"email","attachment_file":None,"attachment_file_name":None,"for":None,"message":"<p><br></p><p>Dear <strong>#name:,</strong></p><p>Welcome to #company:</p><p><br>Some of the company policy documents are attached with this mail. Before you start working in the office, kindly go through to all of them and get a clear understanding of company policies, work culture and environment.</p><p>Once you are well versed with them, you can proceed with your work. In case of any doubt feel free to contact.<br>#hr_signature:<br>#logo:</p>","message_key":"Important HR guidelines and Company Policies","message_origin":"RECRUIT","message_subject":"Important Information - #company:","version":5,"working":True,"default":False,"version_details":[{"message":"<p><br></p><p>Dear <strong>#name:,</strong></p><p>Welcome to #company:</p><p><br>Some of the company policy documents are attached with this mail. Before you start working in the office, kindly go through to all of them and get a clear understanding of company policies, work culture and environment.</p><p>Once you are well versed with them, you can proceed with your work. In case of any doubt feel free to contact.<br>#hr_signature:<br>#logo:</p>","version":1},{"message":"<p><br></p><p>Dear <strong>#name:,</strong></p><p>Welcome to #company:</p><p><br>Some of the company policy documents are attached with this mail. Before you start working in the office, kindly go through to all of them and get a clear understanding of company policies, work culture and environment.</p><p>Once you are well versed with them, you can proceed with your work. In case of any doubt feel free to contact.<br>#hr_signature:<br>#logo:</p>","version":2},{"message":"<p><br></p><p>Dear <strong>#name:,</strong></p><p>Welcome to #company:</p><p><br>Some of the company policy documents are attached with this mail. Before you start working in the office, kindly go through to all of them and get a clear understanding of company policies, work culture and environment.</p><p>Once you are well versed with them, you can proceed with your work. In case of any doubt feel free to contact.<br>#hr_signature:<br>#logo:</p>","version":3},{"message":"<p><br></p><p>Dear <strong>#name:,</strong></p><p>Welcome to #company:</p><p><br>Some of the company policy documents are attached with this mail. Before you start working in the office, kindly go through to all of them and get a clear understanding of company policies, work culture and environment.</p><p>Once you are well versed with them, you can proceed with your work. In case of any doubt feel free to contact.<br>#hr_signature:<br>#logo:</p>","version":4}],"recruit_details":None,"attachment_files":[{"file_id":"72d741fb-f568-4659-b6c1-80f8af2e0e4f","file_name":"block2_3.png","file":"/home/python/projects/notification_system/attached_documents/block2_3.png"},{"file_id":"c4a46a1d-11d6-4a36-a3f9-8984c6e3f4b2","file_name":"block2_4.png","file":"/home/python/projects/notification_system/attached_documents/block2_4.png"},{"file_id":"20cc5ef1-89ac-4392-a3e9-fb1b757fce57","file_name":"block2_3.png","file":"/home/python/projects/notification_system/attached_documents/block2_3.png"},{"file_id":"9d10b8ee-2b3d-4449-a1ab-d1a61bbff8dd","file_name":"block2_1.png","file":"/home/python/projects/notification_system/attached_documents/block2_1.png"}]}
        mongo.db.mail_template.insert_one(payload).inserted_id

        # act
        response = self.app.get(f'/message/triggers?account-name='+account_name,headers={"Secretkey":str(secret_key)})
        jsonResponse = self.json_of_response(response)

        # assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(dict,type(jsonResponse))
        self.assertGreater(len(jsonResponse),0)
        self.assertIn('triggers', jsonResponse)

    
    #Test case for get email template api
    def test_get_email_templates(self):
        payload = {"Doc_type":"email","for":"Interviwee Hold","message":"<p>Dear Applicant<br/>Hope you are doing good!<br/>This is to inform you that with respect your application and subsequent interview with #company: your candidature has been put on hold for a while due to unavoidable circumstance.<br/>We will surely get back to you once the position re-opens. Thank you so much for showing your pleasant interest with the company and the job.<br/>Regards<br/> #hr_signature: </p>","message_key":"interviewee_onhold","message_origin":"RECRUIT","message_subject":"interviewee put on hold","recruit_details":"Interviewee On Hold","version":1,"working":True,"template_head":"5f0c16db3fbe9cf9946700df"}
        mongo.db.mail_template.insert_one(payload)

        #making data
        self.create_mail_variables()

        payload = {"name":"test_letter_head","footer_value":"<div id=\"footer\" style=\"bottom: 0; position: absolute; width: 100%;\"><hr /> <div>ExcellenceTechnosoft Pvt Ltd</div> <div>CIN: U72200DL2010PTC205087</div> <div>Corp Office:C84-A, Sector 8,Noida, U.P. - 201301</div> <div>Regd Office: 328 GAGAN VIHAR IST MEZZAZINE,NEW DELHI-110051</div> <div style=\"height: 5px; margin-top: 5px; margin-bottom: 2px; background-color: #4bb698;\">&nbsp;</div> </div>","header_value":"<p> <div id=\"header\"> <div style=\"height: 5px; background-color: #4bb698;\">&nbsp;</div> <div style=\"height: 8px; margin-top: 1px; background-color: #4bb698;\">&nbsp;</div> <div style=\"height: 5px; margin-top: 1px; background-color: #4bb698;\">&nbsp;</div> <br /> <div style=\"text-align: right; padding-right:40px\"><img src=\"https://res.cloudinary.com/dp0y84e66/image/upload/v1568791251/logo.e5be347d_yf4q90.png\" style=\"width: 150px;\" /></div> </div>","working":True}

        # act
        response = self.app.get(f'/message/get_email_template?account-name='+account_name,headers={"Secretkey":str(secret_key)})
        jsonResponses = self.json_of_response(response)

        # assert
        self.assertEqual(response.status_code, 200)
        for jsonResponse in jsonResponses:
            self.assertIn('message', jsonResponse)
            self.assertIn('message_key', jsonResponse)
            self.assertIn('message_origin', jsonResponse)
            self.assertIn('message_subject', jsonResponse)
            self.assertIn('template_variables', jsonResponse)
    
