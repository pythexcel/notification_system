from app import mongo
import requests
from slackclient import SlackClient
from app.config import default,mail_settings
from flask_mail import Message,Mail
from app import mail
from flask import current_app   


def serialize_doc(doc):
    doc["_id"] = str(doc["_id"])
    return doc

def secret_key():
    msg = mongo.db.tms_settings.find_one({
        "secret_key": {"$exists": True}
    }, {"secret_key": 1, '_id': 0})
    secret_key = msg['secret_key']
    return secret_key


#Function for find webhook_url
def tms_load_hook():
    url = mongo.db.tms_settings.find_one({
        "webhook_url": {"$exists": True}
    }, {"webhook_url": 1, '_id': 0})
    web_url = url['webhook_url']
    return web_url
#function for send mesg 
def slack_message(msg=None,attachments=None):
    slackmsg = {"text": msg,"attachments":attachments}
    webhook_url = tms_load_hook()
    response = requests.post(
        webhook_url, json=slackmsg,
        headers={'Content-Type': 'application/json'})

def slack_attach(msg):
    slackmsg = {"text": msg,
                "attachments": [
        {
            "fallback": "Please add report manually",
            "actions": [
                {
                    "type": "button",
                    "text": "Submit an automatic weekly report",
                    "url": "http://tms.excellencetechnologies.in/#/app/automateWeekly"
                }
            ]
        }
    ]
    }
    webhook_url = load_hook()
    response = requests.post(
        webhook_url, json=slackmsg,
        headers={'Content-Type': 'application/json'})

#function for find slack_token
def tms_load_token():
    token = mongo.db.tms_settings.find_one({
        "slack_token": {"$exists": True}
    }, {"slack_token": 1, '_id': 0})
    sl_token = token['slack_token']
    return sl_token

def slack_msg(channel, msg,attachments):
    slack_token = tms_load_token()
    sc = SlackClient(slack_token)
    for data in channel:
        sc.api_call(
            "chat.postMessage",
            channel=data,
            text=msg,
            attachments=attachments,
            username = "TMS"
        )
def send_email(email,message): 
   app = current_app._get_current_object()
   subject = 'Thank you for registering to our site'
   message = message
   sendere = app.config['MAIL_USERNAME']
   recipient = [email,]
   msg = Message(message,sender=sendere,recipients=recipient)
   mail.send(msg)


def notifie_user(email=None,message=None,attachments=None):
    slack_message(attachments=attachments)
    mail_msg = message.replace("@Slack_id:", email)
    send_email(email=email,message=mail_msg)




def load_monthly_manager_reminder():
    msg = mongo.db.schdulers_msg.find_one({
        "monthly_manager_reminder": {"$exists": True}
    }, {"monthly_manager_reminder": 1, '_id': 0})
    if msg is not None:
        manager_reminder = msg['monthly_manager_reminder']
        return manager_reminder
    else:
        reminder=default['monthly_manager_reminder']
        return reminder

def load_weekly_notes():
    msg = mongo.db.schdulers_msg.find_one({
        "weekly_report_notes": {"$exists": True}
    }, {"weekly_report_notes": 1, '_id': 0})
    if msg is not None:
        manager_reminder = msg['weekly_report_notes']
        return manager_reminder
    else:
        reminder=default['weekly_report_notes']
        return reminder
        
#function for find monthly_reminder mesg from db
def load_monthly_remainder():
    msg = mongo.db.schdulers_msg.find_one({
        "monthly_remainder": {"$exists": True}
    }, {"monthly_remainder": 1, '_id': 0})
    if msg is not None:    
        load_monthly_remainder = msg['monthly_remainder']
        return load_monthly_remainder
    else:
        monthly_remainder=default['monthly_remainder']
        return monthly_remainder


def load_missed_review():
    msg = mongo.db.schdulers_msg.find_one({
        "missed_reviewed_mesg": {"$exists": True}
    }, {"missed_reviewed_mesg": 1, '_id': 0})
    if msg is not None:
        manager_reminder = msg['missed_reviewed_mesg']
        return manager_reminder
    else:
        reminder=default['missed_reviewed_mesg']
        return reminder


def missed_checkin():
    msg = mongo.db.schdulers_msg.find_one({
        "missed_checkin": {"$exists": True}
    }, {"missed_checkin": 1, '_id': 0})
    if msg is not None:
        missed_checkin = msg['missed_checkin']
        return missed_checkin
    else:
        checkin=default['missed_checkin']
        return checkin

def load_monthly_report_mesg():
    msg = mongo.db.schdulers_msg.find_one({
        "monthly_report_mesg": {"$exists": True}
    }, {"monthly_report_mesg": 1, '_id': 0})
    if msg is not None:
        review_msg = msg['monthly_report_mesg']
        return review_msg
    else:
        rev_msg=default["monthly_report_mesg"]
        return rev_msg


def load_weekly_report_mesg():
    msg = mongo.db.schdulers_msg.find_one({
        "weekly_report_mesg": {"$exists": True}
    }, {"weekly_report_mesg": 1, '_id': 0})
    if msg is not None:
        review_msg = msg['weekly_report_mesg']
        return review_msg
    else:
        rev_msg=default["weekly_report_mesg"]
        return rev_msg

#function for find review_activity mesg from db
def load_review_activity():
    msg = mongo.db.schdulers_msg.find_one({
        "review_activity": {"$exists": True}
    }, {"review_activity": 1, '_id': 0})
    if msg is not None:
        review_msg = msg['review_activity']
        return review_msg
    else:
        rev_msg=default["review_activity"]
        return rev_msg

#function for find first two days weekly remienderr mesg
def load_weekly1():
    msg = mongo.db.schdulers_msg.find_one({
        "weekly_remainder1": {"$exists": True}
    }, {"weekly_remainder1": 1, '_id': 0})
    if msg is not None:
        weekly_msg = msg['weekly_remainder1']
        return weekly_msg
    else:
        week_mesg=default["weekly_remainder1"]
        return week_mesg

#function for find first two days weekly remienderr mesg
def load_weekly2():
    msg = mongo.db.schdulers_msg.find_one({
        "weekly_remainder2": {"$exists": True}
    }, {"weekly_remainder2": 1, '_id': 0})
    if msg is not None:
        weekly_msg2 = msg['weekly_remainder2']
        return weekly_msg2
    else:
        week_mesg2=default['weekly_remainder2']
        return week_mesg2        