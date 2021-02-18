
import os
import sys    
import random
import re
#from app import mongo
from app.util.serializer import serialize_doc
import datetime
import dateutil.parser
from bson.objectid import ObjectId
from app.model.validate_smtp import validate_smtp_counts
from app.util.validate_smtp import validate_smtp
from app.email.model.sendmail import send_email
from flask import current_app as app
from dotenv import load_dotenv
import uuid
import time
import email
import requests
from email_validator import validate_email, EmailNotValidError
from dns import resolver 
import dns
import socket 
import smtplib


def MailValidator(mongo):
    verificationstatus = mongo.campaigns.find_one({"verification":"Running"})
    if verificationstatus:
        status = mongo.campaign_users.find({"is_verified":False,"campaign":str(verificationstatus['_id'])}).limit(5)
        emails = [serialize_doc(doc) for doc in status]
        if emails:
            for emaildata in emails:
                try:
                    valid = validate_email(emaildata['email'],check_deliverability=True)
                    email = valid.email
                    try:
                        emailvalid = Emailvalidate(emaildata['email'])
                    except Exception:
                        emailvalid = False

                    if emailvalid == True:
                        try:
                            response = requests.get(
                                "https://isitarealemail.com/api/email/validate",
                                params = {'email': emaildata['email']})
                            status = response.json()['status']
                            if not status == "valid":
                                mongo.campaign_users.update({"_id": ObjectId(emaildata['_id'])},{
                                    "$set":{
                                        "status" : False
                                    }
                                })
                        except Exception:
                            pass
                    else:
                        mongo.campaign_users.update({"_id": ObjectId(emaildata['_id'])},{
                            "$set":{
                                "status" : False
                            }
                        })
                except EmailNotValidError as e:
                    mongo.campaign_users.update({"_id": ObjectId(emaildata['_id'])},{
                        "$set":{
                            "status" : False
                        }
                    })
                mongo.campaign_users.update({"_id": ObjectId(emaildata['_id'])},{
                    "$set":{
                        "is_verified" : True
                    }
                })
        else:
            mongo.campaigns.update({"_id": ObjectId(verificationstatus['_id'])},{
                "$set":{
                    "verification" : "Completed"
                }
            })


def Emailvalidate(email_address):
    #Step 1: Check email
    #Check using Regex that an email meets minimum requirements, throw an error if not
    addressToVerify = email_address
    match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', addressToVerify)

    if match == None:
        return False
    #Step 2: Getting MX record
    #Pull domain name from email address
    domain_name = email_address.split('@')[1]

    #get the MX record for the domain
    records = dns.resolver.query(domain_name, 'MX')
    mxRecord = records[0].exchange
    mxRecord = str(mxRecord)

    #Step 3: ping email server
    #check if the email address exists

    # Get local server hostname
    host = socket.gethostname()

    # SMTP lib setup (use debug level for full output)
    server = smtplib.SMTP()
    server.set_debuglevel(0)

    # SMTP Conversation
    server.connect(mxRecord)
    server.helo(host)
    server.mail(email_address)
    code, message = server.rcpt(str(addressToVerify))
    server.quit()

    # Assume 250 as Success
    if code == 250:
        return True
    else:
        return False

def campaign_mail(mongo):
    APP_ROOT = os.path.join(os.path.dirname(__file__), '..')
    dotenv_path = os.path.join(APP_ROOT, '.env')
    load_dotenv(dotenv_path)
    campaigns = mongo.campaigns.find({"status":"Running"})
    campaigns = [serialize_doc(doc) for doc in campaigns]
    for campaign in campaigns:
        if campaign is not None:
            message_subject_details = []
            if 'message_detail' in campaign:
                if campaign['message_detail']:
                    highest_count_message = max(campaign['message_detail'], key=lambda x:x['count'])
                    for message_detail in campaign['message_detail']:
                        if message_detail['count'] == highest_count_message['count']:
                            message_subject_details.append(message_detail)
                    
            campaign_users = mongo.campaign_users.find({"campaign":campaign['_id'], "unsubscribe_status" : False,"status":True})
            campaign_users = [serialize_doc(doc) for doc in campaign_users]
            total_users = 0
            for user in campaign_users:
                if user is not None: 
                    status = mongo.campaign_users.find_one({"_id":ObjectId(user['_id'])})
                    if status['block'] is False:
                        if 'mail_cron' in status and status['mail_cron'] is False:
                            try:
                                validate = validate_smtp_counts(campaign['smtps'],mongo)
                            except Exception as error:
                                campaign_status_err = mongo.campaigns.update({"_id":ObjectId(campaign['_id'])},
                                        {
                                            "$set": {
                                                    "status": repr(error)
                                                }
                                        })
                                return None
                            else:
                                mail_server = validate['mail_server']
                                mail_port = validate['mail_port']
                                mail_username = validate['mail_username']
                                mail_password = validate['mail_password']
                                count_details = validate['count_details']
                                final_message = random.choice(message_subject_details)
                                mail = user['email']
                                if "pytest" in sys.modules:
                                    mail = mail
                                else:
                                    if os.getenv('ENVIRONMENT') == "development":
                                        full_domain = re.search("@[\w.]+", mail)  
                                        domain = full_domain.group().split(".")
                                        if domain[0] == "@excellencetechnologies":
                                            mail = mail
                                        else:
                                            mail = os.getenv('to')
                                
                                unique = str(user['_id'])
                                filelink = None
                                if 'attachment_file_name' in final_message:
                                    filelink = final_message['attachment_file']
                                filename = None
                                if 'attachment_file' in final_message:
                                    filename = final_message['attachment_file_name']

                                
                                system_variable = mongo.mail_variables.find({})
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
                                    if detail in campaign:
                                        rexWithString = '#' + re.escape(detail) + r'([!]|[@]|[\$]|[\%]|[\^]|[\&]|[\*]|[\:]|[\;])'
                                        message_str = re.sub(rexWithString, campaign[detail], message_str)
                                    elif detail in user:
                                        rexWithString = '#' + re.escape(detail) + r'([!]|[@]|[\$]|[\%]|[\^]|[\&]|[\*]|[\:]|[\;])'
                                        message_str = re.sub(rexWithString, user[detail], message_str)
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
                                    if detail in campaign:
                                        rexWithString = '#' + re.escape(detail) + r'([!]|[@]|[\$]|[\%]|[\^]|[\&]|[\*]|[\:]|[\;])'
                                        message_subject = re.sub(rexWithString, campaign[detail], message_subject)
                                    elif detail in user:
                                        rexWithString = '#' + re.escape(detail) + r'([!]|[@]|[\$]|[\%]|[\^]|[\&]|[\*]|[\:]|[\;])'
                                        message_str = re.sub(rexWithString, user[detail], message_str)
                                    else:
                                        for element in system_variable:
                                            if "#" + detail == element['name'] and element['value'] is not None:
                                                rexWithSystem = re.escape(element['name']) + r'([!]|[@]|[\$]|[\%]|[\^]|[\&]|[\*]|[\:]|[\;])' 
                                                message_subject = re.sub(rexWithSystem, element['value'], message_subject)  
                                digit = str(uuid.uuid4())
                                to = []
                                if mail not in to:
                                    to.append(mail)
                                working_status = True
                                try:        
                                    send_email(message=message_str,
                                    recipients=to,
                                    subject=message_subject,
                                    user=unique,
                                    campaign=str(campaign['_id']),
                                    sending_mail= mail_username,
                                    sending_password= mail_password,
                                    sending_server= mail_server,
                                    digit=digit,
                                    campaign_message_id=final_message['message_id'],
                                    filelink=filelink,
                                    filename=filename,
                                    sending_port= mail_port)
                                except Exception as error:
                                    if total_users == 3:
                                        error = mongo.campaigns.update({"campaign_id": campaign['_id']},{
                                            "$pull":{
                                                "smtps": mail_server
                                            }
                                        })
                                        return None
                                    else:
                                        total_users +=1
                                        campaing_user_failed = mongo.campaign_users.update({"_id":ObjectId(user['_id'])},
                                        {
                                            "$set": {
                                                    "send_status": True,
                                                    "mail_cron": True,
                                                    "successful":  False,
                                                    "error_message" : repr(error),
                                                    "error_time": datetime.datetime.now()
                                            }
                                        })
                                    working_status = False   
                                else:  
                                    mail_data = mongo.mail_status.insert_one({
                                        "user_mail": user['email'],
                                        "user_id": str(user['_id']),
                                        "sending_time": datetime.datetime.utcnow(),
                                        "message": message_str,
                                        "mail_sended_status": working_status,
                                        "subject":message_subject,
                                        "recipients": to,
                                        "digit": digit,
                                        "campaign": str(campaign['_id']),
                                        "sending_mail": mail_username,
                                        "sending_password":mail_password,
                                        "sending_server":mail_server,
                                        "seen": False,
                                        "sending_port":mail_port,
                                        "clicked": False,
                                        "bounce_type":"pending",
                                        "bounce": False
                                    }).inserted_id
                                    smtp_val = mongo.smtp_count_validate.update({"_id": ObjectId(count_details)},{
                                        "$inc": {
                                            "count": 1
                                            }
                                    })

                                    user_status = mongo.campaign_users.update({"_id":ObjectId(user['_id'])},
                                        {
                                            "$set": {
                                                    "send_status": True,
                                                    "mail_cron": True,
                                                    "successful":  working_status,
                                                    "sended_date": datetime.datetime.now()
                                            },
                                                "$push": {
                                                    "mail_message": {
                                                    "sended_message_details": digit,
                                                    "campaign": str(campaign['_id'])
                                                }
                                            }
                                        })
                                    # finding if campaign have no user left which mail is needed to be send mark it as completed
                                    user_available = mongo.campaign_users.aggregate([{ "$match" : {"campaign":campaign['_id']}},{ "$group": { "_id": None, "count": { "$sum": 1 } } }])
                                    user_available = [serialize_doc(doc) for doc in user_available]

                                    user_completed = mongo.campaign_users.aggregate([{ "$match" : {"campaign":campaign['_id'],"send_status":True,"mail_cron":True}},{ "$group": { "_id": None, "count": { "$sum": 1 } } }])
                                    user_completed = [serialize_doc(doc) for doc in user_completed]
                                    
                                    for data in user_available:
                                        for element in user_completed:
                                            if data['count'] == element['count']:
                                                campaign_status = mongo.campaigns.update({"_id":ObjectId(campaign['_id'])},
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
                else:
                    pass
        else:
            pass
