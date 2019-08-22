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

    return (sl_conv_list['user']['id'])


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


                            
   
   