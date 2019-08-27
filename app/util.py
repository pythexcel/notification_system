from app import mongo
import requests
from slackclient import SlackClient
from app.mail_util import send_email
from flask import jsonify
import datetime
from app.slack_util import slack_id,slack_message
from app.mail_util import send_email

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
            missing_payload.append(data)
    if not missing_payload:
        construct_message(message=message,message_variables=message_variables,
                        req_json=req_json,system_require=system_require,message_detail=message_detail)             
    else:
        ret = ",".join(missing_payload)
        raise Exception("These data are missing from payload: " + ret)      



def construct_message(message=None,req_json=None,message_variables=None,system_require=None,message_detail=None):
    system_variable ={"Date":datetime.datetime.utcnow().strftime("%d-%B-%Y")}
    status = mongo.db.slack_settings.find_one({},{"_id":0})
    if status['slack_notfication'] is True:
        slack = slack_id(req_json['user']['email'])
        req_json['user'] = "<@" + slack + ">!"
        message_str = message
        for data in message_variables:
            if data in req_json:
                message_str = message_str.replace("@"+data+":", req_json[data])
        for elem in system_require:
            if elem in system_variable:  
                message_str = message_str.replace("@"+elem+":", system_variable[elem])            
        slack_message(message=message_str,channel=message_detail['slack_channel'])
    else:
        pass
    if status['send_email'] is True:
        req_json['user'] = req_json['user']['email']
        message_str = message
        for data in message_variables:
            if data in req_json:
                message_str = message_str.replace("@"+data+":", req_json[data])
        for elem in system_require:
            if elem in system_variable:  
                message_str = message_str.replace("@"+elem+":", system_variable[elem])            
        send_email(message=message_str,recipients=message_detail['email_group'],subject=message_detail['message_key'])
    else:
        pass

      
