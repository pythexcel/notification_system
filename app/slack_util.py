from app import mongo
import requests
from slackclient import SlackClient
from app.mail_util import send_email
from app.config import system_variable


def slack_load_token():
    token = mongo.db.slack_settings.find_one({
        "slack_token": {"$exists": True}
    }, {"slack_token": 1, '_id': 0})
    sl_token = token['slack_token']
    return sl_token

def slack_message(channel, msg,attachments):
    slack_token = slack_load_token()
    sc = SlackClient(slack_token)
    for data in channel:
        sc.api_call(
            "chat.postMessage",
            channel=data,
            text=msg,
            attachments=attachments
        )

def Notify_user(user=None,message=None,req_json=None):
    message_special = message.split()
    special = []
    for data in message_special:
        if data[0]=='@':
            special.append(data[1:-1])
    message_str = message
    for data in special:
        system_var = False
        for elem in system_variable:
            if data == elem:
                print(elem + "-----" +data)
                system_var =True
                message_str = message_str.replace("@"+data+":", system_variable[data])
        if not system_var:
            for detail in req_json:
                if data == detail:
                    message_str = message_str.replace("@"+data+":", req_json[data])        
    print(message_str)
    
    slack_message(attachments=attachments)
    