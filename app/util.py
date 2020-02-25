from app import mongo
import requests
from slackclient import SlackClient
from app.mail_util import send_email
from flask import jsonify
import datetime
from app.slack_util import slack_id,slack_message
from app.mail_util import send_email
import json
from bson.objectid import ObjectId
import re

def serialize_doc(doc):
    doc["_id"] = str(doc["_id"])
    return doc

def user_data(campaign_details):
    details = mongo.db.campaign_users.find({"campaign":campaign_details['_id']})
    details = [serialize_doc(doc) for doc in details]
    
    for data in details:
        hit_data = []
        if 'mail_message' in data:
            for element in data['mail_message']:
                if element['campaign'] == campaign_details['_id']:
                    hit_details = mongo.db.mail_status.find_one({"digit": element['sended_message_details']},
                    {
                        "hit_rate":1,
                        "message":1,
                        "mail_sended_status":1,
                        "seen_date":1,
                        "sending_time": 1,
                        "subject": 1,
                        "seen": 1 ,
                        "clicked": 1,
                        "bounce_type":1
                    })
                    if hit_details is not None:
                        hit_details['_id'] = str(hit_details['_id'])
                        if hit_details not in hit_data:
                            hit_data.append(hit_details)
                    bounce_status = hit_details['bounce_type']
        data['hit_details'] = hit_data
        data['mail_message'] = None
        data['bounce_type'] = bounce_status

    campaign_details['users'] = details

    validate = mongo.db.campaign_clicked.find({"campaign_id": campaign_details['_id']})
    if validate:
        clicking_details = mongo.db.campaign_clicked.aggregate([
            {
            "$project": 
            {   "clicked_time": 1,
                "campaign_id": 1,
                "time":{
                "$switch":
                {
                "branches": [
                    {
                    "case": { "$and" : [ { "$gte" : [ {  "$hour" : "$clicked_time" },0 ] },
                                    { "$lt" : [ { "$hour" : "$clicked_time" },6 ] } ] },
                    "then": "morning"
                    },
                    {
                    "case": { "$and" : [ { "$gte" : [ {  "$hour" : "$clicked_time" },6 ] },
                                    { "$lt" : [ { "$hour" : "$clicked_time" },12 ] } ] },
                    "then": "noon"
                    },
                    {
                    "case": { "$and" : [ { "$gte" : [ {  "$hour" : "$clicked_time" },12 ] },
                                    { "$lt" : [ { "$hour" : "$clicked_time" },18 ] } ] },
                    "then": "evening"
                    },
                    {
                    "case": { "$and" : [ { "$gte" : [ {  "$hour" : "$clicked_time" },18 ] },
                                    { "$lt" : [ { "$hour" : "$clicked_time" },24 ] } ] },
                    "then": "night"
                    }
                ],
                "default": "No record found."
                } 
                }}},
                {
                "$match": {"campaign_id": campaign_details['_id']}
                },
                { "$group": { "_id": {"interval":"$time","date":"$clicked_time"}, "myCount": { "$sum": 1 } } },
                { "$sort" : { "_id.date" : 1 } }
                ])
        clicking_data = []
        currDate = None
        currMonth = None
        for data in clicking_details:
            if currDate is None or currMonth != data['_id']['date'].month and currDate == data['_id']['date'].day or currDate != data['_id']['date'].day:
                clicking_data.append([data])
            else:
                clicking_data[len(clicking_data)-1].append(data) 
            currMonth = data['_id']['date'].month 
            currDate = data['_id']['date'].day
            
        campaign_details['clicking_details'] = clicking_data
    else:
        campaign_details['clicking_details'] = []
    return campaign_details

def validate_message(user=None,message=None,req_json=None,message_detail=None):
    system_variable ={"Date":datetime.datetime.utcnow().strftime("%d-%B-%Y")}
    message_special = message.split()
    message_variables = []
    system_require = []
    missing_payload = []
    rex = re.compile('\@[a-zA-Z0-9/_]+\:')
    for data in message_special:
        reg = rex.match(data)
        if reg is not None:
            vl = data.find(":") - len(data)
            message_variables.append(data[1:vl])                              
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
    system_variable ={"Date":datetime.datetime.utcnow().strftime("%d-%B-%Y")}
    status = mongo.db.slack_settings.find_one({},{"_id":0})
    req_json = json.loads(json.dumps(req_json))
    slack_user_detail = req_json
    req_json = json.loads(json.dumps(req_json))
    email_user_detail = req_json
    slack = ""
    slack_details = None
    if message_detail['for_email'] is False:
        if 'user' in slack_user_detail and slack_user_detail['user'] is not None:
            try:
                slack = slack_id(slack_user_detail['user']['email'])
            except Exception:
                slack_details = False   
            if slack_details is False:    
                slack_user_detail['user'] = slack_user_detail['user']['name']
            else:    
                slack_user_detail['user'] = "<@" + slack + ">"
        else:
            pass            
        message_str = message
        for data in message_variables:
            if data in slack_user_detail:
                if slack_user_detail[data] is None:
                    slack_user_detail[data] = "N/A"
                message_str = message_str.replace("@"+data+":", slack_user_detail[data])
            else:
                if data in slack_user_detail['data']:
                    if slack_user_detail['data'][data] is None:
                        slack_user_detail['data'][data] = "N/A"
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
        if message_detail['sended_to'] == "private":
            channels.append(slack)
        else:
            pass      
        if channels:                                                   
            mongo.db.messages_cron.insert_one({
                "cron_status":False,
                "type": "slack",
                "message":message_str,
                "channel":channels,
                "req_json": slack_user_detail,
                "message_detail":message_detail
            }).inserted_id
        else:
            pass
    else:
        pass

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
            mongo.db.messages_cron.insert_one({
                "cron_status":False,
                "type": "email",
                "message":message_str,
                "recipients":recipient,
                "subject": subject
            }).inserted_id
        else:
            pass
    else:
        pass
    
# this function will send back variables of html templates with variable from templates if there are None in special variables collection
def template_requirement(user):
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
    message = user['message'].split("#")
    del message[0]
    message_variables = []
    rex = re.compile('!|@|\$|\%|\^|\&|\*|\:|\;')
    for elem in message:
        varb = re.split(rex, elem)
        if "#" + varb[0] in special_val:
            message_variables.append(varb[0])    
        if varb[0] not in message_variables:
            if "#" + varb[0] not in unrequired:
                message_variables.append(varb[0])
    for data in message_variables:
        if data not in unique_variables:
            unique_variables.append(data) 
    message_str = user['message']
    header = None
    footer = None
    if 'template_head' in user:
        var = mongo.db.letter_heads.find_one({"_id":ObjectId(user['template_head'])})
        if var is not None:
            header = var['header_value']
            footer = var['footer_value']
        if header is not None:
            header_rex = re.escape("#page_header") + r'([!]|[@]|[\$]|[\%]|[\^]|[\&]|[\*]|[\:]|[\;])' 
            message_str = re.sub(header_rex, header, message_str)
        if footer is not None:
            footer_rex = re.escape("#page_footer") + r'([!]|[@]|[\$]|[\%]|[\^]|[\&]|[\*]|[\:]|[\;])' 
            message_str = re.sub(footer_rex, footer, message_str)

    if 'template_head' in user:
        ret = mongo.db.letter_heads.find({"_id":ObjectId(user['template_head'])})
        ret = [serialize_doc(doc) for doc in ret]
        user['template_head'] = [ret]
    else:
        pass   
                                  
    user['message'] = message_str
    user['template_variables'] = unique_variables 
    return user              

def Template_details(details):
    users = 0
    Template_data = []
    user_data = mongo.db.campaign_users.aggregate([{ "$match" : {"campaign":details['_id']}},{ "$group": { "_id": None, "count": { "$sum": 1 } } }])
    user_data = [serialize_doc(doc) for doc in user_data]
    if user_data:
        for data in user_data:
            users = data['count']
    details['users'] = users    
    if 'Template' in details:
        for elem in details['Template']:
            ret = mongo.db.mail_template.find_one({"_id":ObjectId(elem)})
            ret = serialize_doc(ret)
            Template_data.append(ret)
        details['Template'] = Template_data
    else:
        pass
    return details

def campaign_details(user):
    name = user['campaign']
    ret = mongo.db.campaigns.find_one({"_id": ObjectId(name)})
    if ret is not None:
        user['campaign'] = serialize_doc(ret)
    else:
        user['campaign'] = None
    return user   

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif','docx','doc'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS