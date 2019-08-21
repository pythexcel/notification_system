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

def construct_message(user=None,message=None,req_json=None):
    date_time = datetime.datetime.utcnow()
    formatted_date = date_time.strftime("%d-%B-%Y")
    system_variable ={"Date":formatted_date}
    message_special = message.split()
    special = []
    missing_payload = []
    for data in message_special:
        if data[0]=='@':
            special.append(data[1:-1])
    print(special)
    need_found_in_payload = True
    for data in special:
        need_found_in_payload = False
        for elem in req_json:
            print(data, elem)
            if data == elem:
                need_found_in_payload = True
        if need_found_in_payload == False:
            missing_payload.append(data)     
    if len(missing_payload) <= 0:
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
                    print(detail + "-----" +data)
                    if data == detail:
                        message_str = message_str.replace("@"+data+":", req_json[data])
        print(message_str)
        return jsonify("message created"),200                        
    else:
        structure = ","
        ret = structure.join(missing_payload)
        return jsonify(ret + " is missing from request"), 400        
                
                            
   
   