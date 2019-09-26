from app import mongo
import requests
from slackclient import SlackClient
from app.mail_util import send_email
from flask import jsonify
import datetime

def slack_load_token():
    token = mongo.db.slack_settings.find_one({
        "slack_token": {"$exists": True}
    }, {"slack_token": 1, '_id': 0})
    sl_token = token['slack_token']
    return sl_token

def slack_id(email):
    slack_token = slack_load_token()
    sc = SlackClient(slack_token)
    sl_user_id = sc.api_call("users.lookupByEmail",
                       email=email)
    print(sl_user_id['user']['id'])                   

    return (sl_user_id['user']['id'])


def slack_message(channel, message,req_json=None,message_detail=None):
    slack_token = slack_load_token()
    sc = SlackClient(slack_token)
    if 'button' in req_json:
        color = None
        if 'color' in  req_json['button']:
            color = req_json['button']['color']        
        attachments = [
            {
            "fallback": "fallback",
            "color" : color, 
            "actions" : req_json['button']['actions']
            }
        ]
    else:
        attachments = None                 
    if message_detail['message_color'] is not None:
        color = message_detail['message_color']
        attachments = [
            {
            "fallback": "fallback",
            "color" : color,
            "text": message 
            }
        ]
        message = None    
    else:
        pass
    for data in channel:
        print(data)
        sc.api_call(
            "chat.postMessage",
            channel=data,
            text=message,
            attachments=attachments
        )


def slack_profile(email=None):
    print(email)
    slack_token = slack_load_token()
    sc = SlackClient(slack_token)
    sl_user_id = sc.api_call("users.lookupByEmail",
                       email=email)

    return (sl_user_id['user'])
                              