import re
#from app import mongo
from app.util.serializer import serialize_doc
import datetime
import dateutil.parser
from bson.objectid import ObjectId
from app.email.model.sendmail import send_email
from app.slack.model.slack_util import slack_message
from flask import current_app as app
import time
import email
import requests
from app.utils import fetching_validated_account
from app.account import initDB



def cron_messages():
    accounts,account_config = fetching_validated_account()
    for account in accounts:  
        account_mongo = account_config[account]
        mongo = initDB(account,account_mongo)
        if mongo is not None:
            ret = mongo.messages_cron.find_one({"cron_status":False,"message_detail.message_origin":"HR"})
            if ret is not None:
                vet = mongo.messages_cron.update({"_id":ObjectId(ret['_id'])},
                    {
                        "$set": {
                                "cron_status": True
                            }
                            })

                if ret['type'] == "email":
                    send_email(mongo,message=ret['message'],recipients=ret['recipients'],subject=ret['subject'])
                elif ret['type'] == "slack":
                    slack_message(mongo,message=ret['message'],channel=ret['channel'],req_json=ret['req_json'],message_detail=ret['message_detail'])
                else:
                    pass    
            else:
                pass 


def tms_cron_messages():
    accounts,account_config = fetching_validated_account()
    for account in accounts:  
        account_mongo = account_config[account]
        mongo = initDB(account,account_mongo)
        if mongo is not None:
            ret = mongo.messages_cron.find_one({"cron_status":False,"message_detail.message_origin":"TMS"})
            if ret is not None:
                vet = mongo.messages_cron.update({"_id":ObjectId(ret['_id'])},
                    {
                        "$set": {
                                "cron_status": True
                            }
                            })

                if ret['type'] == "email":
                    send_email(mongo,message=ret['message'],recipients=ret['recipients'],subject=ret['subject'])
                elif ret['type'] == "slack":
                    slack_message(mongo,message=ret['message'],channel=ret['channel'],req_json=ret['req_json'],message_detail=ret['message_detail'])
                else:
                    pass    
            else:
                pass 



def recruit_cron_messages():
    accounts,account_config = fetching_validated_account()
    for account in accounts:  
        account_mongo = account_config[account]
        mongo = initDB(account,account_mongo)
        if mongo is not None:
            ret = mongo.messages_cron.find_one({"cron_status":False,"message_detail.message_origin":"RECRUIT"})
            if ret is not None:
                vet = mongo.messages_cron.update({"_id":ObjectId(ret['_id'])},
                    {
                        "$set": {
                                "cron_status": True
                            }
                            })

                if ret['type'] == "email":
                    if "sender_name" in ret:
                        sender_name = ret['sender_name']
                    else:
                        sender_name = None
                    print("8999999999999999999",ret['message'])
                    send_email(mongo,message=ret['message'],recipients=ret['recipients'],subject=ret['subject'],sender_name=sender_name)
                elif ret['type'] == "slack":
                    slack_message(mongo,message=ret['message'],channel=ret['channel'],req_json=ret['req_json'],message_detail=ret['message_detail'])
                else:
                    pass    
            else:
                pass 


#Zapier cron for fetch payload from collection and hit webhook
def zapier_cron_messages(mongo):
    ret = mongo.messages_cron.find_one({"zapier_cron_status":False,"type":"zapier"})
    if ret is not None:
        vet = mongo.messages_cron.update({"_id":ObjectId(ret['_id'])},
            {
                "$set": {
                        "zapier_cron_status": True
                    }
                    })
        #calling function webhook which will return avaliable webhook from db by notification message key
        hookurlDetails = webhook(mongo,data=ret)
        if hookurlDetails is not None:
            hookurl = hookurlDetails['webhook']
            payload = {'slackmessage': ret['slackmessage'], "defaultmessage": ret['defaultmessage'], "recipients": ret['recipients'], "channel": ret['channel'], "phone":ret['phone'], "subject":ret['subject']}
            #hitting webhhok this will send notification to all integrated apps with this webhook.
            #Like we want to send checkin notification to mail and phone number then we have integrated both apps with this webhook 
            #this will send notification to both apps
            response = requests.post(url=hookurl, json=payload)
            output = response.json()
        else:
            pass
    else:
        pass



#Webhook function which will return webhook by message key
def webhook(mongo,data=None):
    if data is not None:
        if 'message_detail' in data:
            message_key = data['message_detail']['message_key']
            ret = mongo.webhooks.find_one({"message_key":message_key})
            return ret
        else:
            return None
    else:
        return None
