from app import mongo
import requests
from slackclient import SlackClient
from app.mail_util import send_email

def serialize_doc(doc):
    doc["_id"] = str(doc["_id"])
    return doc

def secret_key():
    msg = mongo.db.slack_tokens.find_one({
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

def slack_attach(msg,attachments):
    slackmsg = {"text": msg,
                "attachments": attachments
    }
    webhook_url = tms_load_hook()
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

def notifie_user(email=None,message=None,color=None,data=None):
    message_special = message.split()
    special = []
    for data in message_special:
        if data[0]=='@':
            special.append(data[1:-1])

    # logic needs to be right here for replacing the special characters with request value or static values
    slack_message(attachments=attachments)
    mail_msg = message.replace("@Slack_id:", email)
    send_email(email=email,message=mail_msg)