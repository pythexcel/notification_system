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
from app.config import message_needs
import re
import dateutil.parser

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
                        "bounce": 1,
                        "bounce_type" : 1
                    })
                    if hit_details is not None:
                        hit_details['_id'] = str(hit_details['_id'])
                        if hit_details not in hit_data:
                            hit_data.append(hit_details)
        data['hit_details'] = hit_data
        data['mail_message'] = None

    campaign_details['users'] = details

    validate = mongo.db.campaign_clicked.find({"campaign_id": campaign_details['_id']})
    if validate:
        clicking_details = mongo.db.campaign_clicked.aggregate([
            {
            "$project": 
            {   "clicked_time": 1,
                "campaign_id": 1,
                "month": { "$month": "$clicked_time" },
                "day": { "$dayOfMonth": "$clicked_time" },
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
                { "$group": { "_id": {"interval":"$time","month":"$month","day":"$day"}, "myCount": { "$sum": 1 },"clicking_date" : {"$first": "$clicked_time"} } },
                { "$sort" : { "clicking_date" : -1 } }
                ])
        clicking_data = []
        currDate = None
        currMonth = None
        for data in clicking_details:
            if currDate is None or (currMonth != data['_id']['month'] and currDate == data['_id']['day']) or (currDate != data['_id']['day']):
                clicking_data.append({'date': data['clicking_date'], data['_id']['interval']: data['myCount'] })
            else:
                clicking_data[-1][data['_id']['interval']] = data['myCount']
            currMonth = data['_id']['month']
            currDate = data['_id']['day']
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
    req_json = json.loads(json.dumps(req_json))
    zapier_user_detail = req_json
    slack = ""
    slack_details = None
    # If for_slack is true in request which coming from tms it will send notification to slack using exist slack apis functionality.
    if message_detail['for_slack'] is True:
        if 'user' in slack_user_detail and slack_user_detail['user'] is not None:
            try:
                slack = slack_id(slack_user_detail['user']['email']) # Fetching user slack id by email using slack api
            except Exception:
                slack_details = False   
            #If there is slack id available then it will put slack it in message else will put username
            if slack_details is False:    
                slack_user_detail['user'] = slack_user_detail['user']['name']
            else:    
                slack_user_detail['user'] = "<@" + slack + ">"
        else:
            pass            
        # I make common function for message create and replace all data @data: variables according to requested notification from tms
        #This function will return us proper message with slack id which need to send to user.
        message_str = MakeMessage(message_str=message,message_variables=message_variables,slack_user_detail=slack_user_detail,system_require=system_require,system_variable=system_variable)
        #I make a common function for fetch channels from tms requests.like on which slack or personal we want to send message.
        channels = FetchChannels(slack_user_detail=slack_user_detail,message_detail=message_detail)
        #If channels available for send notification it will insert notification info in collection.
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

    # If for_email is true in request which coming from tms it will send notification to email using exist email functionality i didn't make any change in this.
    if message_detail['for_email'] is True:
        if 'user' in email_user_detail and email_user_detail['user'] is not None:
            username = json.loads(json.dumps(email_user_detail['user']['email']))
            name = username.split('@')[0]
            email_user_detail['user'] = name
        else:
            pass    
        # I make common function for message create and replace all data @data: variables according to requested notification from tms
        #This function will return us proper message with username which need to send to user.
        message_str = MakeMessage(message_str=message,message_variables=message_variables,slack_user_detail=email_user_detail,system_require=system_require,system_variable=system_variable)
        #I make a common function for fetch recipients from tms requests.like on which email we want to send message.
        recipient = FetchRecipient(slack_user_detail=email_user_detail,message_detail=message_detail)
        if 'subject' in email_user_detail['emailData']:
            subject = email_user_detail['emailData']['subject']
        else:
            subject = message_detail['message_key']
        #If channels available for send notification it will insert notification info in collection.
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
    # If for_zapier is true in request which coming from tms it will send notification to zapier using webhook.
    if message_detail['for_zapier'] is True:
        email = ""
        #Fetching username from tms request data.
        if "user" in zapier_user_detail:
            username = zapier_user_detail['user']['name']
        else:
            username = ""
        #Fetching email id for send email to notification related user
        if "work_email" in zapier_user_detail['user']:
            email = zapier_user_detail['user']['work_email']
        else:
            if "email" in zapier_user_detail['user']:
                email = zapier_user_detail['user']['email']
            else:
                pass
        #If email data is available in message request like notification subject etc defined already and its available in db in message it will take subject from there 
        #Else message key will be email subject.
        if 'emailData' in zapier_user_detail:
            if 'subject' in zapier_user_detail['emailData']:
                subject = zapier_user_detail['emailData']['subject']
            else:
                subject = message_detail['message_key']             
        else:
            subject = message_detail['message_key']             
        #For phone data if phone details availabl in request it will take phone number from there.
        if 'PhoneData' in zapier_user_detail:
            phone = zapier_user_detail['PhoneData']
        else:
            phone = ""

        #Here we are making two messages one for send to slack and on for default can send any other platform.
        #Difference between both just in slack message have slack if and in default message have username.
        if 'user' in zapier_user_detail and zapier_user_detail['user'] is not None:
            try:
                slack = slack_id(zapier_user_detail['user']['email'])# Fetching user slack id by email using slack api
            except Exception:
                slack_details = False   
            #If there is slack id available then it will put slack it in message else will put username
            if slack_details is False:    
                zapier_user_detail['user'] = zapier_user_detail['user']['name']
            else:    
                zapier_user_detail['user'] = "<@" + slack + ">"
        else:
            pass            
        # I make common function for message create and replace all data @data: variables according to requested notification from tms
        #This function will return us proper message with user slackid which need to send to user.
        slackmessage = MakeMessage(message_str=message,message_variables=message_variables,slack_user_detail=zapier_user_detail,system_require=system_require,system_variable=system_variable)
        #I make a common function for fetch channels from tms requests.like on which slack or personal we want to send message.
        channels = FetchChannels(slack_user_detail=zapier_user_detail,message_detail=message_detail)

        if slack_details is not False:
                zapier_user_detail['user'] = username
        else:
            pass
        #calling same function for make default message with username instead of slack id 
        defaultmessage = MakeMessage(message_str=message,message_variables=message_variables,slack_user_detail=zapier_user_detail,system_require=system_require,system_variable=system_variable)
        #I make a common function for fetch recipients from tms requests.like on which email we want to send message.
        recipient = FetchRecipient(slack_user_detail=zapier_user_detail,message_detail=message_detail)
        #if no default recipients available then it will take user email.
        if not recipient:
            recipient = [email]
        #Will inser mesaage payload in collection from there zapier cron will take it and hit webhook
        if channels or recipient is not None:
            mongo.db.messages_cron.insert_one({
                "cron_status":False,
                "type": "zapier",
                "slackmessage":slackmessage,
                "defaultmessage":defaultmessage,
                "recipients":recipient,
                "channel":channels,
                "phone":phone,
                "subject": subject,
                "req_json": zapier_user_detail,
                "message_detail":message_detail
            }).inserted_id
        else:
            pass
    else:
        pass
    

# Common function for fetch channels form tms request
def FetchChannels(slack_user_detail=None,message_detail=None):
    slack = ""
    channels = []          
    #It will take slack channels if slack channel available in user details
    if 'slack_channel' in slack_user_detail:
        for data in slack_user_detail['slack_channel']:
            channels.append(data)
    else:
        pass  
    #It will take slack channels if slack channel available in message details
    if message_detail['slack_channel'] is not None:
        for elem in message_detail['slack_channel']:
            channels.append(elem)       
    #It will take slack channels if sended status private like slack bot
    if message_detail['sended_to'] == "private":
        channels.append(slack)
    else:
        pass      
    #will return array of slack channels
    return channels


#function for fetch recipients if email group email available in message request it will fetch all mails and return array
def FetchRecipient(slack_user_detail=None,message_detail=None):
    recipient = []
    if 'email_group' in slack_user_detail:
        for data in slack_user_detail['email_group']:
            recipient.append(data)
    else:
        pass
    if message_detail['email_group'] is not None:
        for elem in message_detail['email_group']:
            recipient.append(elem)
    return recipient


#function for make message from message request.
#This function will replace all @data: valiables with requested data and will make a proper message with username or slackid as same as before nothing change in this
def MakeMessage(message_str=None,message_variables=None,slack_user_detail=None,system_require=None,system_variable=None):
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
    return message_str
    
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



def contruct_payload_from_request(message_detail=None,input=None):
    if message_detail and input is not None:
        if 'message' in message_detail:
            message = message_detail['message']
            missing_payload = []
            # looping over all the needs check if my message type in that key and if found
            for key in message_needs:
                if message_detail['message_type'] == key:
                    need_found_in_payload = False
                    # LOOP OVER THE KEYS inside the need FOR REQUEST
                    for data in message_needs[key]:
                        need_found_in_payload = False
                        if data in input:
                            need_found_in_payload = True
                        # REQUIREMNT DOES NOT SATISFIED RETURN INVALID REQUEST
                        else:
                            missing_payload.append(data)
                            # return jsonify(data + " is missing from request"), 400
                    # IF FOUND PROCESS THE REQUEST.JSON DATA
                    if not missing_payload:
                        try:
                            validate_message(message=message,message_detail=message_detail,req_json=input) 
                            return True
                        except Exception as error:
                            return(repr(error)),400
                    else:
                        ret = ",".join(missing_payload)
                        raise Exception(ret + " is missing from request")
        else:
            raise Exception("Message not available in message details")
    else:
        raise Exception("MessageDetails and input not should be None")


def convert_dates_to_format(dates_converter=None,req=None):
    if dates_converter is not None:
        for elem in dates_converter:
            if elem in req['data']:
                if req['data'][elem] is not None:
                    if req['data'][elem] != "":
                        if req['data'][elem] != "No Access":
                            date_formatted = dateutil.parser.parse(req['data'][elem]).strftime("%d %b %Y")
                            req['data'][elem] = date_formatted    
        return req
    raise Exception("Dates not should be none in request")