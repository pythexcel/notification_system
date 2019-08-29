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

    return (sl_user_id['user']['id'])


def slack_message(channel, message,req_json=None):
    slack_token = slack_load_token()
    sc = SlackClient(slack_token)
    if 'button_text' and 'url_link' in req_json:
        attachments = [
                {"fallback": "Please add report manually",  
                "actions": [
                        {
                        "type": "button",
                        "text": req_json['button_text'],
                        "url": req_json['url_link']
                        }
                ]}]
    else:
        attachments = None            
    for data in channel:
        sc.api_call(
            "chat.postMessage",
            channel=data,
            text=message,
            attachments=attachments
        )


                            
   
   