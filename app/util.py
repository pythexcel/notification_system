from app import mongo
import requests
from slackclient import SlackClient
from app.mail_util import send_email
from flask import jsonify
import datetime

def serialize_doc(doc):
    doc["_id"] = str(doc["_id"])
    return doc


def construct_message(user=None,message=None,req_json=None):
    system_variable ={"Date":datetime.datetime.utcnow().strftime("%d-%B-%Y")}
    message_special = message.split()
    message_variables = []
    missing_payload = []
    for data in message_special:
        if data[0]=='@':
            message_variables.append(data[1:-1])
    for data in system_variable:
        if data in message_variables:
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
        message_str = message
        for data in message_variables:
            system_var = False
            for elem in system_variable:
                if data == elem:
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
        ret = ",".join(missing_payload)
        return jsonify(ret + " is missing from request"), 400        
                    