import re
import datetime
from app.config import dates_converter
from app.util.serializer import serialize_doc
from bson.objectid import ObjectId
from flask import current_app as app




def attach_letter_head( header, footer, message):
    download_pdf = "#letter_head #content #letter_foot"
    if header is not None:
        download_pdf = download_pdf.replace("#letter_head", header)
    else:
        download_pdf = download_pdf.replace("#letter_head", '')
    download_pdf = download_pdf.replace("#content", message)
    if footer is not None:
        download_pdf = download_pdf.replace("#letter_foot", footer)
    else:
        download_pdf = download_pdf.replace("#letter_foot", '')
    return download_pdf



#payload going = {"message_detail":"message string","request":"data variable","system_variable":"mail template"}
def generate_full_template_from_string_payload(message_detail=None, request=None,system_variable=None):
    missing_payload = []
    message_str,missing_payload = construct_message_str(message_detail= message_detail['message'], request=request['data'],system_variable=system_variable)
    missing_payload.extend(missing_payload)
    mobile_message_str = construct_mobile_message_str(message_detail=message_detail,request=request,system_variable=system_variable)
    message_subject,missing_payload = construct_message_subject(message_detail=message_detail,request=request,system_variable=system_variable)
    missing_payload.extend(missing_payload)
    return message_str,message_subject,mobile_message_str,missing_payload


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
    return message_str,missing_payload

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
    if 'message_subject' in message_detail:
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
        return message_subject,missing_payload
    else:
        raise Exception("message subject not available in request")

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


