import re
import datetime
from app import mongo
from app.config import dates_converter
from app.util import serialize_doc
from bson.objectid import ObjectId
from flask import current_app as app

#function for get notification message by message key
def get_notification_function_by_key(MSG_KEY = None):
    if MSG_KEY is not None: 
        message_detail = mongo.db.notification_msg.find_one({"message_key": MSG_KEY})
        if message_detail is not None:
            return message_detail
        else:
            raise Exception("No message available for this key")
    else:
        raise Exception("Message key is none")



def construct_attachments_in_by_msg_details(message_detail=None,req=None):
    attachment_file = None
    attachment_file_name = None
    if 'attachment' in req:
        if 'attachment_file' in message_detail:
            attachment_file = message_detail['attachment_file']
        if 'attachment_file_name' in message_detail:
            attachment_file_name = message_detail['attachment_file_name']
    else:
        pass    
    
    files = None

    if 'attachment_files' in message_detail:
        if message_detail['attachment_files']:
            files = message_detail['attachment_files']

    header = None
    footer = None
    if 'template_head' in message_detail:        
        var = mongo.db.letter_heads.find_one({"_id":ObjectId(message_detail['template_head'])})
        if var is not None:
            header = var['header_value']
            footer = var['footer_value']
    return attachment_file,attachment_file_name,files,header,footer



#payload going = {"message_detail":"message string","request":"data variable","system_variable":"mail template"}
def generate_full_template_from_string_payload(message_detail=None, request=None,system_variable=None):
    missing_payload = []

    construct_msg = construct_message_str(message_detail= message_detail['message'], request= request.json['data'],system_variable=system_variable)
    message_str = construct_msg.get('message')
    missing_payload.extend(construct_msg.get('missing_payload'))

    mobile_message_str = construct_mobile_message_str(message_detail=message_detail,request=request.json,system_variable=system_variable)

    construct_msg_sub = construct_message_subject(message_detail=message_detail,request=request,system_variable=system_variable)
    message_subject = construct_msg_sub.get('message_subject')
    missing_payload.extend(construct_msg_sub.get('missing_payload'))

    return {'message':message_str,'message_subject':message_subject,'mobile_message_str':mobile_message_str,'missing_payload': missing_payload }


#function for filter and return message string and missing payload by message details
def construct_message_str( message_detail=None, request=None ,system_variable=None):
    message_variables = []
    message = message_detail.split('#')
    del message[0]
    message_regex = re.compile('!|@|\$|\%|\^|\&|\*|\:')
    for keyword in message:
        message_keyword = re.split(message_regex, keyword)
        message_variables.append(message_keyword[0])
    message_str = message_detail
    for detail in message_variables:
        if detail in request:
            if request[detail] is not None:
                rexWithString = '#' + re.escape(detail) + r'([!]|[@]|[\$]|[\%]|[\^]|[\&]|[\*]|[\:])'
                message_str = re.sub(rexWithString, str(request[detail]), message_str)
        else:
            for element in system_variable:
                if "#" + detail == element['name'] and element['value'] is not None:
                    rexWithSystem = re.escape(element['name']) + r'([!]|[@]|[\$]|[\%]|[\^]|[\&]|[\*]|[\:])' 
                    message_str = re.sub(rexWithSystem, str(element['value']), message_str)    
    missing = message_str.split('#')
    del missing[0]
    missing_payload = convert_response_to_payload(missing=missing)
    return { 'message': message_str, 'missing_payload': missing_payload }

#function for filter and return mobile message string and missing payload by message details
def construct_mobile_message_str(message_detail=None,request=None,system_variable=None):
    mobile_message_str = None
    if 'mobile_message' in message_detail:
        mobile_variables = []
        mobile_message = message_detail['mobile_message'].split('#')
        del mobile_message[0]
        mob_rex = re.compile('!|@|\$|\%|\^|\&|\*|\:')
        for elem in mobile_message:
            mob_varb = re.split(mob_rex, elem)
            mobile_variables.append(mob_varb[0])
        mobile_message_str = message_detail['mobile_message']
        for detail in mobile_variables:
            if detail in request['data']:
                if request['data'][detail] is not None:
                    rexWithString = '#' + re.escape(detail) + r'([!]|[@]|[\$]|[\%]|[\^]|[\&]|[\*]|[\:])'
                    mobile_message_str = re.sub(rexWithString, str(request['data'][detail]), mobile_message_str)
            else:
                for element in system_variable:
                    if "#" + detail == element['name'] and element['value'] is not None:
                        rexWithSystem = re.escape(element['name']) + r'([!]|[@]|[\$]|[\%]|[\^]|[\&]|[\*]|[\:])' 
                        mobile_message_str = re.sub(rexWithSystem, str(element['value']), mobile_message_str)    
        return mobile_message_str
    else:
        return mobile_message_str #just because not raise an exeption here because if no mobile message available
                        #it should move with none because no data available of users mobile in our system it will raise every time exception


#function for filter and return message subject and missing payload by message details
def construct_message_subject(message_detail=None,request=None,system_variable=None):
    subject_variables = []
    message_sub = message_detail['message_subject'].split('#')
    del message_sub[0]
    regex = re.compile('!|@|\$|\%|\^|\&|\*|\:')
    for elem in message_sub:
        sub_varb = re.split(regex, elem)
        subject_variables.append(sub_varb[0])
    message_subject = message_detail['message_subject']
    for detail in subject_variables:
        if detail in request['data']:
            if request['data'][detail] is not None:
                rexWithString = '#' + re.escape(detail) + r'([!]|[@]|[\$]|[\%]|[\^]|[\&]|[\*]|[\:])'
                message_subject = re.sub(rexWithString, str(request['data'][detail]), message_subject)

        else:
            for element in system_variable:
                if "#" + detail == element['name'] and element['value'] is not None:
                    rexWithSystem = re.escape(element['name']) + r'([!]|[@]|[\$]|[\%]|[\^]|[\&]|[\*]|[\:])' 
                    message_subject = re.sub(rexWithSystem, str(element['value']), message_subject)  
    missing_subject = message_subject.split("#")
    del missing_subject[0]
    missing_payload = convert_response_to_payload(missing=missing_subject)
    return { 'message_subject': message_subject, 'missing_payload': missing_payload }


#function for find missing values from payload
def convert_response_to_payload(missing=None):
    missing_payload = []
    missing_regex_value = re.compile('!|@|\$|\%|\^|\&|\*|\:')
    for elem in missing:
        missing_data = re.split(missing_regex_value, elem)
        missing_payload.append({"key": missing_data[0] , "type": "date" if missing_data[0] in dates_converter else "text"})
    return missing_payload



def fetch_msg_and_subject_by_date(request=None,message_str=None,message_subject=None):
    if 'fromDate' in request['data'] and request['data']['fromDate'] is not None:
        if 'toDate' in request['data'] and request['data']['toDate'] is not None:
            if request['data']['fromDate'] == request['data']['toDate']:
                message_str = message_str.replace(request['data']['fromDate'] + " to " + request['data']['toDate'],request['data']['fromDate'])

    if 'fromDate' in request['data'] and request['data']['fromDate'] is not None:
        if 'toDate' in request['data'] and request['data']['toDate'] is not None:
            if request['data']['fromDate'] == request['data']['toDate']:
                message_subject = message_subject.replace(request['data']['fromDate'] + " to " + request['data']['toDate'],request['data']['fromDate'])
    return message_str,message_subject



#function for fetch details from db by date about interview reminders
def fetch_interview_reminders(date=None):
    if date is not None:
        details = mongo.db.reminder_details.aggregate([
            { '$match' : {
                'date': { '$gte' : date }
            }},
        {
            '$group' : {
                '_id' : {
                    '$dateToString': { 'format': "%Y-%m-%d", 'date': "$date" }} , 'total' : { '$sum' : 1}
            }},
            { '$sort': { '_id': 1 } }
            ])
        details =[serialize_doc(doc) for doc in details]
        return details
    else:
        raise Exception("Date not should be None")



#Here function for fetch recipients according to env
def fetch_recipients_by_mode(request=None):
    if request is not None:
        MAIL_SEND_TO = None     
        if app.config['ENV'] == 'development':
            for email in request.get('to'):
                full_domain = re.search("@[\w.]+", email)
                domain = full_domain.group().split(".")
                if domain[0] == "@excellencetechnologies":
                    MAIL_SEND_TO = [email]
                else:
                    MAIL_SEND_TO = [app.config['to']]
        else:
            if app.config['ENV'] == 'production':
                MAIL_SEND_TO = request.get("to",None)
        return MAIL_SEND_TO
    else:
        raise Exception("Request not should be None")


#function for update messages into collection
def update_recruit_mail_msg(phone=None,phone_message=None,phone_issue=None,message=None,subject=None,to=None,is_reminder=None):
    if message and subject and to is not None:
        id = mongo.db.recruit_mail.update({"message":message,"subject":subject,"to":to},{
        "$set":{
            "phone":phone,
            "phone_message": phone_message,
            "phone_issue": phone_issue,
            "message": message,
            "subject": subject,
            "to":to,
            "is_reminder":is_reminder,
            "date": datetime.datetime.now()
        }},upsert=True)
    else:
        raise Exception("Message subject and recipents not should be none")
