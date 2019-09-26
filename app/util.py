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
    print(message_variables)        
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
            # HERE the logic behind this is if someone wants to send multiple things in req then variable data will be a dictionary
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
    print("conc message")
    system_variable ={"Date":datetime.datetime.utcnow().strftime("%d-%B-%Y")}
    status = mongo.db.slack_settings.find_one({},{"_id":0})
    req_json = json.loads(json.dumps(req_json))
    slack_user_detail = req_json
    req_json = json.loads(json.dumps(req_json))
    email_user_detail = req_json
    if status['slack_notfication'] is True:
        print("sdasd")
        # this condition if written if message is just for mail but will remove this if not required
        if message_detail['for_email'] is False:
            print('hai isme')
            if 'user' in slack_user_detail and slack_user_detail['user'] is not None:
                slack = slack_id(slack_user_detail['user']['email'])
                slack_user_detail['user'] = "<@" + slack + ">"
            else:
                pass            
            message_str = message
            print(message_str)
            for data in message_variables:
                if data in slack_user_detail:
                    message_str = message_str.replace("@"+data+":", slack_user_detail[data])
                else:
                    if data in slack_user_detail['data']:
                        message_str = message_str.replace("@"+data+":", slack_user_detail['data'][data])    
            for elem in system_require:
                if elem in system_variable:  
                    message_str = message_str.replace("@"+elem+":", system_variable[elem])
            channels = []          
            if 'slack_channel' in slack_user_detail:
                for data in slack_user_detail['slack_channel']:
                    channels.append(data)
            else:
                pass  
            if message_detail['slack_channel'] is not None:
                for elem in message_detail['slack_channel']:
                    channels.append(elem)
            # here is the conditon for sending message to just the user himself as we discussed there will be 2 condtion for public/private               
            if message_detail['sended_to'] == "private":
                channels.append(slack)
            else:
                pass  
            print(channels)    
            if channels:                                                        
                slack_message(message=message_str,channel=channels,req_json=slack_user_detail,message_detail=message_detail)   
            else:
                pass
        else:
            pass
    else:
        pass
    if status['send_email'] is True:
        # same condition for if just send to mail will remove if not required
        if message_detail['for_email'] is True:
            if 'user' in email_user_detail and email_user_detail['user'] is not None:
                username = json.loads(json.dumps(email_user_detail['user']['email']))
                name = username.split('@')[0]
                email_user_detail['user'] = name
            else:
                pass    
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

            recipient = []
            if 'email_group' in email_user_detail:
                for data in email_user_detail['email_group']:
                    recipient.append(data)
            else:
                pass
            if message_detail['sended_to'] == "private":
                recipient.append(username)
            else:
                pass  

            if message_detail['email_group'] is not None:
                for elem in message_detail['email_group']:
                    recipient.append(elem)

            if 'subject' in email_user_detail['emailData']:
                subject = email_user_detail['emailData']['subject']
            else:
                subject = message_detail['message_key']             
            if recipient:
                send_email(message=message_str,recipients=recipient,subject=subject)
            else:
                pass
        else:
            pass
    else:
        pass


# this function will send back variables of html templates with variable from templates if there are None in special variables collection
def special(user):
    special_val = []
    unrequired = []
    unique_variables = []
    ret = mongo.db.mail_variables.find({})
    ret = [serialize_doc(doc) for doc in ret]
    for data in ret:
        if data['value'] is None:
            special_val.append(data['name'])
        if data['value'] is not None:
            unrequired.append(data['name'])
    message = user['message']
    message_variables = []
    message = message.split()
    for elem in message:
        if "#" + elem[1:] in special_val:
            message_variables.append(elem[1:])    
        if elem[0] == "#":
            if elem[1:] not in message_variables :
                if "#" + elem[1:] not in unrequired:
                    message_variables.append(elem[1:])

    for data in message_variables:
        if data not in unique_variables:
            unique_variables.append(data)                    
    user['template_variables'] = unique_variables 
    return user              

      
