from app import mongo
import requests
from slackclient import SlackClient
from app.mail_util import send_email
from flask import jsonify
import datetime
from app.slack_util import slack_id,slack_message
from app.mail_util import send_email
import json


def serialize_doc(doc):
    doc["_id"] = str(doc["_id"])
    return doc


def validate_message(user=None,message=None,req_json=None,message_detail=None):
    system_variable ={"Date":datetime.datetime.utcnow().strftime("%d-%B-%Y")}
    message_special = message.split()
    message_variables = []
    system_require = []
    missing_payload = []
    for data in message_special:
        if data[0]=='@':
            message_variables.append(data[1:-1])
    for data in system_variable:
        if data in message_variables:
            system_require.append(data)
            message_variables.remove(data)
        else:
            pass        
    need_found_in_payload = True
    for data in message_variables:
        need_found_in_payload = False
        if data in req_json:
            need_found_in_payload = True
        else:
            if data in req_json['data']:
                need_found_in_payload = True
            else:
                missing_payload.append(data)
    if not missing_payload:
        construct_message(message=message,message_variables=message_variables,
                        req_json=req_json,system_require=system_require,message_detail=message_detail)             
    else:
        ret = ",".join(missing_payload)
        raise Exception("These data are missing from payload: " + ret)      



def construct_message(message=None,req_json=None,message_variables=None,system_require=None,message_detail=None):
    print(req_json)
    system_variable ={"Date":datetime.datetime.utcnow().strftime("%d-%B-%Y")}
    status = mongo.db.slack_settings.find_one({},{"_id":0})
    req_json = json.loads(json.dumps(req_json))
    slack_user_detail = req_json
    req_json = json.loads(json.dumps(req_json))
    email_user_detail = req_json
    if status['slack_notfication'] is True:
        if message_detail['slack_channel'] is not None:
            slack = slack_id(slack_user_detail['user']['email'])
            slack_user_detail['user'] = "<@" + slack + ">!"        
            message_str = message
            for data in message_variables:
                if data in slack_user_detail:
                    message_str = message_str.replace("@"+data+":", slack_user_detail[data])
                else:
                    if data in slack_user_detail['data']:
                        message_str = message_str.replace("@"+data+":", slack_user_detail['data'][data])    
            for elem in system_require:
                if elem in system_variable:  
                    message_str = message_str.replace("@"+elem+":", system_variable[elem])  
            if 'slack_channel' in slack_user_detail:
                channel = slack_user_detail['slack_channel']
            else:
                channel = message_detail['slack_channel']                                              
            slack_message(message=message_str,channel=channel,req_json=slack_user_detail)
        else:
            pass    
    else:
        pass
    if status['send_email'] is True:
        if message_detail['email_group'] is not None:
            print(email_user_detail['user']['email'])
            email_user_detail['user'] = email_user_detail['user']['email']
            message_str = message
            for data in message_variables:
                if data in email_user_detail:
                    message_str = message_str.replace("@"+data+":", email_user_detail[data])
                else:
                    if data in email_user_detail['data']:
                        message_str = message_str.replace("@"+data+":", email_user_detail['data'][data])
            for elem in system_require:
                if elem in system_variable:  
                    message_str = message_str.replace("@"+elem+":", system_variable[elem])
            if 'email_group' in slack_user_detail:
                recipients = email_user_detail['email_group']
            else:
                recipients = message_detail['email_group']                                 
            send_email(message=message_str,recipients=recipients,subject=message_detail['message_key'])
        else:
            pass
    else:
        pass


      
