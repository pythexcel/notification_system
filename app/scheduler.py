import os
import random
import re
from app import mongo
from app.util import serialize_doc
import datetime
import dateutil.parser
from bson.objectid import ObjectId
from app.mail_util import send_email,validate_smtp_counts
from app.slack_util import slack_message
from flask import current_app as app
from dotenv import load_dotenv
import uuid
import time

def campaign_mail():
    APP_ROOT = os.path.join(os.path.dirname(__file__), '..')
    dotenv_path = os.path.join(APP_ROOT, '.env')
    load_dotenv(dotenv_path)
    campaigns = mongo.db.campaigns.find({"status":"Running"})
    campaigns = [serialize_doc(doc) for doc in campaigns]
    for campaign in campaigns:
        if campaign is not None:
            message_subject_details = []
            if campaign['message'] != "":
                if campaign['message_subject'] != "":
                    message_subject_details.append({"message":campaign['message'],"message_subject":campaign["message_subject"]})
            if 'Template' in campaign:
                template_data = random.choice(campaign['Template'])
                Template_details = mongo.db.mail_template.find_one({"_id":ObjectId(campaign['_id'])})
                message_subject_details.append({"message": Template_details['message'],"message_subject": Template_details["message_subject"]})
            campaign_users = mongo.db.campaign_users.find({"campaign":campaign['_id'],"blocked":False})
            for user in campaign_users:
                if user is not None:
                    final_message = random.choice(message_subject_details)
                    mail = user['email']
                    if os.getenv('ENVIRONMENT') == "development":
                        mail = os.getenv('to')
                    unique = str(user['_id'])

                    system_variable = mongo.db.mail_variables.find({})
                    system_variable = [serialize_doc(doc) for doc in system_variable]
                    subject = final_message['message_subject']
                    message_variables = []
                    message = final_message['message'].split('#')
                    del message[0]
                    rex = re.compile('!|@|\$|\%|\^|\&|\*|\:|\;')
                    for elem in message:
                        varb = re.split(rex, elem)
                        message_variables.append(varb[0])
                    message_str = final_message['message']
                    for detail in message_variables:
                        if detail in ret:
                            rexWithString = '#' + re.escape(detail) + r'([!]|[@]|[\$]|[\%]|[\^]|[\&]|[\*]|[\:]|[\;])'
                            message_str = re.sub(rexWithString, ret[detail], message_str)
                        else:
                            for element in system_variable:
                                if "#" + detail == element['name'] and element['value'] is not None:
                                    rexWithSystem = re.escape(element['name']) + r'([!]|[@]|[\$]|[\%]|[\^]|[\&]|[\*]|[\:]|[\;])' 
                                    message_str = re.sub(rexWithSystem, element['value'], message_str)  

                    subject_variables = []
                    message_sub = subject.split('#')
                    del message_sub[0]
                    regex = re.compile('!|@|\$|\%|\^|\&|\*|\:|\;')
                    for elem in message_sub:
                        sub_varb = re.split(regex, elem)
                        subject_variables.append(sub_varb[0])
                    message_subject = subject
                    for detail in subject_variables:
                        if detail in ret:
                            rexWithString = '#' + re.escape(detail) + r'([!]|[@]|[\$]|[\%]|[\^]|[\&]|[\*]|[\:]|[\;])'
                            message_subject = re.sub(rexWithString, ret[detail], message_subject)
                        else:
                            for element in system_variable:
                                if "#" + detail == element['name'] and element['value'] is not None:
                                    rexWithSystem = re.escape(element['name']) + r'([!]|[@]|[\$]|[\%]|[\^]|[\&]|[\*]|[\:]|[\;])' 
                                    message_subject = re.sub(rexWithSystem, element['value'], message_subject)  


                    digit = str(uuid.uuid4())
                    to = []
                    to.append(mail)
                    working_status = True
                    try:        
                            send_email(message=message_str,
                            recipients=to,
                            subject=message_subject,
                            user=unique,
                            sending_mail= user['mail_username'],
                            sending_password=user['mail_password'],
                            sending_server=user['mail_server'],
                            digit=digit,
                            sending_port=user['mail_port'])
                        except Exception:
                            working_status = False
                        mail_data = mongo.db.mail_status.insert_one({
                            "user_mail": user['email'],
                            "user_id": str(user['_id']),
                            "sending_time": datetime.datetime.now(),
                            "message": message_str,
                            "mail_sended_status": working_status,
                            "subject":message_subject,
                            "recipients": to,
                            "digit": digit,
                            "campaign": str(campaign['_id']),
                            "sending_mail": user['mail_username'],
                            "sending_password":user['mail_password'],
                            "sending_server":user['mail_server'],
                            "seen": False,
                            "sending_port":user['mail_port'],
                            "clicked": False

                        }).inserted_id
                        smtp_val = mongo.db.smtp_count_validate.update({"_id": ObjectId(user['count_details'])},{
                            "$inc": {
                                "count": 1
                                }
                        })

                        user_status = mongo.db.campaign_users.update({"_id":ObjectId(ret['_id'])},
                            {
                                "$set": {
                                        "send_status": True,
                                        "mail_cron": True,
                                        "successful":  working_status,
                                        "sended_date": datetime.datetime.now(),
                                },
                                    "$push": {
                                        "mail_message": {
                                        "sended_message_details": digit,
                                        "campaign": str(campaign['_id'])
                                    }
                                }
                            })
                        # finding if campaign have no user left which mail is needed to be send mark it as completed
                        user_available = mongo.db.campaign_users.aggregate([{ "$match" : {"campaign":campaign['_id']}},{ "$group": { "_id": None, "count": { "$sum": 1 } } }])
                        user_available = [serialize_doc(doc) for doc in user_available]

                        user_completed = mongo.db.campaign_users.aggregate([{ "$match" : {"campaign":campaign['_id'],"send_status":True}},{ "$group": { "_id": None, "count": { "$sum": 1 } } }])
                        user_completed = [serialize_doc(doc) for doc in user_completed]

                        for data in user_available:
                            for elemetn in user_completed:
                                if data['count'] == element['count']:
                                    campaign = mongo.db.campaigns.update({"_id":ObjectId(campaign['_id'])},
                                        {
                                            "$set": {
                                                    "status": "Completed"
                                                }
                                        })
                                else:
                                    pass
                        time.sleep(campaign['delay'])
                else:
                    pass
        else:
            pass
                
def reject_mail():
    ret = mongo.db.rejection_handling.find_one({"send_status":False})
    if ret is not None:
        mail = ret['email']
        message = ret['message']
        time = ret['rejection_time']  
        time_update = dateutil.parser.parse(time).strftime("%Y-%m-%dT%H:%M:%SZ")
        rejected_time = datetime.datetime.strptime(time_update,'%Y-%m-%dT%H:%M:%SZ')
        diffrence = datetime.datetime.utcnow() - rejected_time
        if diffrence.days >= 1:
            to = []
            to.append(mail)
            send_email(message=message,recipients=to,subject='REJECTED')
            user_status = mongo.db.rejection_handling.remove({"_id":ObjectId(ret['_id'])})
        else:
            pass
    else:
        pass

def cron_messages():
    ret = mongo.db.messages_cron.find_one({"cron_status":False})
    if ret is not None:
        vet = mongo.db.messages_cron.update({"_id":ObjectId(ret['_id'])},
            {
                "$set": {
                        "cron_status": True
                    }
                    })

        if ret['type'] == "email":
            send_email(message=ret['message'],recipients=ret['recipients'],subject=ret['subject'])
        elif ret['type'] == "slack":
            slack_message(message=ret['message'],channel=ret['channel'],req_json=ret['req_json'],message_detail=ret['message_detail'])
        else:
            pass    
    else:
        pass 
        
