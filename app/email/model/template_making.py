#from app import mongo
import requests
from slackclient import SlackClient
from app.email.model.sendmail import send_email
from flask import jsonify
import datetime
import json
from bson.objectid import ObjectId
from app.config import message_needs
import re
import dateutil.parser
from app.util.serializer import serialize_doc
from flask import current_app as app

def construct_attachments_in_by_msg_details(mongo,message_detail=None,req=None):
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
        var = mongo.letter_heads.find_one({"_id":ObjectId(message_detail['template_head'])})
        if var is not None:
            header = var['header_value']
            footer = var['footer_value']
    return attachment_file,attachment_file_name,files,header,footer


# this function will send back variables of html templates with variable from templates if there are None in special variables collection
def template_requirement(user,mongo):
    special_val = []
    unrequired = []
    unique_variables = []
    ret = mongo.mail_variables.find({})
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
        var = mongo.letter_heads.find_one({"_id":ObjectId(user['template_head'])})
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
        ret = mongo.letter_heads.find({"_id":ObjectId(user['template_head'])})
        ret = [serialize_doc(doc) for doc in ret]
        user['template_head'] = [ret]
    else:
        pass   
                                  
    user['message'] = message_str
    user['template_variables'] = unique_variables 
    return user              

def Template_details(details,mongo):
    users = 0
    Template_data = []
    user_data = mongo.campaign_users.aggregate([{ "$match" : {"campaign":details['_id']}},{ "$group": { "_id": None, "count": { "$sum": 1 } } }])
    user_data = [serialize_doc(doc) for doc in user_data]
    if user_data:
        for data in user_data:
            users = data['count']
    details['users'] = users    
    if 'Template' in details:
        for elem in details['Template']:
            ret = mongo.mail_template.find_one({"_id":ObjectId(elem)})
            ret = serialize_doc(ret)
            Template_data.append(ret)
        details['Template'] = Template_data
    else:
        pass
    return details



def assign_letter_heads( letterhead_id ):
    letter_head_details = mongo.db.letter_heads.find_one({ "_id": ObjectId(letterhead_id) })
    if letter_head_details is not None:
        header = letter_head_details['header_value']
        footer = letter_head_details['footer_value']
        return { 'header': header, 'footer': footer }
    else:
        raise Exception("No letterhead available for this letterhead_id")






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



#Here function for fetch recipients according to env
def slack_fetch_recipients_by_mode(request=None):
    if request is not None:
        MAIL_SEND = []     
        if app.config['ENV'] == 'development':
            for email in request.get('to'):
                full_domain = re.search("@[\w.]+", email)
                domain = full_domain.group().split(".")
                if domain[0] == "@excellencetechnologies":
                    MAIL_SEND_TO = [email]
                else:
                    MAIL_SEND_TO = [app.config['to']]
                if MAIL_SEND_TO:
                    MAIL_SEND.append(MAIL_SEND_TO[0])
        else:
            if app.config['ENV'] == 'production':
                MAIL_SEND = request.get("to",None)
        return MAIL_SEND
    else:
        raise Exception("Request not should be None")


