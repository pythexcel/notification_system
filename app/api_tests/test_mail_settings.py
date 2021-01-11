'''
import unittest
from json import dumps
from json.decoder import JSONDecodeError
from requests.exceptions import ConnectionError
import json
from app import mongo
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

    def create_smtp_settings(self):
        payload = {"mail_server":"smtp.mail.yahoo.com","mail_port":587,"origin":"RECRUIT","mail_use_tls":True,"mail_username":"testhr69@yahoo.com","mail_password":"yunbxoxtqhokidef","active":False,"type":"ssl","mail_from":None,"demon_mail":"mailer-daemon@yahoo.com"}
        id = mongo.db.mail_settings.insert_one(payload).inserted_id
        return id


    #testing get mail setting api
    def test_get_mail_settings(self):

        #Making data
        payload = [
                   {"mail_server":"smtp.mail.yahoo.com","mail_port":587,"origin":"RECRUIT","mail_use_tls":True,"mail_username":"testhr69@yahoo.com","mail_password":"yunbxoxtqhokidef","active":False,"type":"ssl","mail_from":None,"demon_mail":"mailer-daemon@yahoo.com"},
                   {"mail_server":"smtp.gmail.com","mail_port":465,"origin":"RECRUIT","mail_use_tls":True,"mail_username":"testnt64@gmail.com","mail_password":"injbjnzckuqjddgm","active":False,"type":"tls","mail_from":None,"demon_mail":"mailer-daemon@googlemail.com"},
                   {"mail_server":"smtp.gmail.com","mail_port":465,"origin":"RECRUIT","mail_use_tls":True,"mail_username":"testhr69@gmail.com","mail_password":"tinngkcaebxlnhhu","active":True,"type":"tls","mail_from":None}
                   ]
        origin = "RECRUIT"
        mongo.db.mail_settings.insert_many(payload)

        #act
        response = self.app.get('/smtp/settings/'+origin,headers={"Secretkey":"gUuWrJauOiLcFSDCL5TM1heITeBVcL"})
        jsonResponse = self.json_of_response(response)

        # assert
        self.assertEqual(response.status_code, 200)
        for jsonResponses in jsonResponse:
            self.assertIn('_id',jsonResponses)
            self.assertIn('active',jsonResponses)
            self.assertIn('mail_from',jsonResponses)
            self.assertIn('mail_port',jsonResponses)
            self.assertIn('mail_server',jsonResponses)
            self.assertIn('mail_use_tls',jsonResponses)
            self.assertIn('mail_username',jsonResponses)
            self.assertIn('origin',jsonResponses)
            self.assertIn('type',jsonResponses)



    #testing delete mail settings api
    def test_delete_mail_settings(self):

        #Making data
        id = self.create_smtp_settings()
        origin = "RECRUIT"

        #act
        response = self.app.delete('/smtp/settings/'+origin+'/'+str(id),headers={"Secretkey":"gUuWrJauOiLcFSDCL5TM1heITeBVcL"})

        #assert
        self.assertEqual(response.status_code, 200)
        self.assertIn('Smtp conf deleted',response.get_data(as_text=True))



    #testing update mail settings api
    def test_update_mail_settings(self):

        #Making data
        id = self.create_smtp_settings()
        origin = "RECRUIT"
        jsonpayload = json.dumps({
            "active": True
        })

        #act
        response = self.app.put('/smtp/settings/'+origin+'/'+str(id),headers={"Content-Type": "application/json","Secretkey":"gUuWrJauOiLcFSDCL5TM1heITeBVcL"}, data=jsonpayload)

        #assert
        self.assertEqual(response.status_code, 200)
        self.assertIn('Smtp conf status changed',response.get_data(as_text=True))



    #testing smtp priority api
    def test_smtp_priority(self):
        position = "1"
        #Making data
        payload = {"mail_server":"smtp.gmail.com","mail_port":465,"origin":"CAMPAIGN","mail_use_tls":True,"mail_username":"etechmusic8@gmail.com","mail_password":"dwxdfpovcucnqcms","active":True,"type":"tls","daemon_mail":"mailer-daemon@googlemail.com","priority":3,"mail_from":None,"created_at":1583338477745}
        id = mongo.db.mail_settings.insert_one(payload).inserted_id

        #act
        response = self.app.post('/smtp/smtp_priority/'+str(id)+'/'+position,headers={"Secretkey":"gUuWrJauOiLcFSDCL5TM1heITeBVcL"})

        self.assertEqual(response.status_code, 200)
        self.assertIn("priority changed",response.get_data(as_text=True))



    def test_update_settings_with_invalid_payload(self):
        origin = "HR"
        
        payload = {"mail_server":"smtp.gmail.com","mail_port":465,"origin":"HR","mail_use_tls":True,"mail_username":"testnt64@gmail.com","mail_password":"injbjnzckuqjddgm","active":True,"type":"tls","priority":1,"mail_from":"testnt64@gmail.com","created_at":1580235746679}

        id = mongo.db.mail_settings.insert_one(payload).inserted_id

        payload = json.dumps({
            "new_password":"test@123"
        })

        #act
        response = self.app.put('/smtp/update_settings/'+origin+'/'+str(id),headers={"Content-Type": "application/json","Secretkey":"gUuWrJauOiLcFSDCL5TM1heITeBVcL"}, data=payload)

        self.assertEqual(response.status_code, 400)



    def test_update_settings(self):
        origin = "HR"
        
        payload = {"mail_server":"smtp.gmail.com","mail_port":465,"origin":"HR","mail_use_tls":True,"mail_username":"testnt64@gmail.com","mail_password":"injbjnzckuqjddgm","active":True,"type":"tls","priority":1,"mail_from":"testnt64@gmail.com","created_at":1580235746679}

        id = mongo.db.mail_settings.insert_one(payload).inserted_id

        payload = json.dumps({
            "new_password":"injbjnzckuqjddgm"
        })

        #act
        response = self.app.put('/smtp/update_settings/'+origin+'/'+str(id),headers={"Content-Type": "application/json","Secretkey":"gUuWrJauOiLcFSDCL5TM1heITeBVcL"}, data=payload)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Smtp password updated",response.get_data(as_text=True))



    #testing validate smtp api
    def test_validate_smtp(self):

        payload = json.dumps({
            "email":"testnt64@gmail.com",
            "password":"injbjnzckuqjddgm"
            })

        #act
        response = self.app.post('/smtp/validate_smtp',headers={"Content-Type": "application/json","Secretkey":"gUuWrJauOiLcFSDCL5TM1heITeBVcL"}, data=payload)

        #assert
        self.assertEqual(response.status_code, 200)
        self.assertIn("login succesfull",response.get_data(as_text=True))



    #testing validate smtp api with invalid crediantials
    def test_validate_smtp_invalid_crediantials(self):
        payload = json.dumps({
            "email":"testnt64@gmail.com",
            "password":"injbjnzcuqjddgm"
            })

        #act
        response = self.app.post('/smtp/validate_smtp',headers={"Content-Type": "application/json","Secretkey":"gUuWrJauOiLcFSDCL5TM1heITeBVcL"}, data=payload)

        self.assertEqual(response.status_code, 400)
        self.assertIn("smtp login and password failed",response.get_data(as_text=True))
'''