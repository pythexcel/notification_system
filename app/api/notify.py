from app import token
from app import mongo
from flask import (Blueprint, flash, jsonify, abort, request,url_for,send_from_directory)
from app.mail_util import send_email
from app.util import serialize_doc,construct_message,validate_message,allowed_file,template_requirement
from app.config import message_needs,dates_converter
from app.slack_util import slack_message,slack_id
from app.sms_util import dispatch_sms
from flask_jwt_extended import (JWTManager, jwt_required, create_access_token,
                                get_jwt_identity, get_current_user,
                                jwt_refresh_token_required,
                                verify_jwt_in_request)
import json
import uuid
import os 
from weasyprint import HTML, CSS
from app.phone_util import Push_notification
from bson.objectid import ObjectId
from werkzeug import secure_filename
from flask import current_app as app
import re
import base64
import bson
import dateutil.parser
import datetime
from datetime import timedelta
import smtplib

bp = Blueprint('notify', __name__, url_prefix='/notify')
        
@bp.route('/dispatch', methods=["POST"])
#@token.authentication
def dispatch():
    if not request.json:
        abort(500)
    MSG_KEY = request.json.get("message_key", None)
    message_detail = mongo.db.notification_msg.find_one({"message_key": MSG_KEY})
    if message_detail and message_detail['message_type'] is not None:   
            message = message_detail['message']
            missing_payload = []
            # looping over all the needs check if my message type in that key and if found
            for key in message_needs:
                if message_detail['message_type'] == key:
                    need_found_in_payload = False
                    # LOOP OVER THE KEYS inside the need FOR REQUEST
                    for data in message_needs[key]:
                        need_found_in_payload = False
                        if data in request.json:
                            need_found_in_payload = True
                        # REQUIREMNT DOES NOT SATISFIED RETURN INVALID REQUEST
                        else:
                            missing_payload.append(data)
                            # return jsonify(data + " is missing from request"), 400
                    # IF FOUND PROCESS THE REQUEST.JSON DATA
                    if not missing_payload:
                        input = request.json
                        try:
                            validate_message(message=message,message_detail=message_detail,req_json=input) 
                            return jsonify({"status":True,"Message":"Sended"}),200 
                        except Exception as error:
                            return(repr(error)),400
                    else:
                        ret = ",".join(missing_payload)
                        return jsonify(ret + " is missing from request"), 400
    else:
        return jsonify("No Message Type Available"), 400

@bp.route('/preview', methods=["POST"])
#@token.admin_required
#@token.authentication
def send_mails():   #Just a big api should use small small functions in api
    if not request.json:
        abort(500)
    for elem in dates_converter:
        if elem in request.json['data']:
            if request.json['data'][elem] is not None:
                if request.json['data'][elem] != "":
                    if request.json['data'][elem] != "No Access":
                        date_formatted = dateutil.parser.parse(request.json['data'][elem]).strftime("%d %b %Y")
                        request.json['data'][elem] = date_formatted    
        
    MSG_KEY = request.json.get("message_key", None)  
    Data = request.json.get("data",None)
    Message = request.json.get("message",None)
    Subject = request.json.get("subject",None)
    message_detail = mongo.db.mail_template.find_one({"message_key": MSG_KEY})
    smtp_email = request.json.get("smtp_email",None)
    phone = request.json.get("phone", None)
    if message_detail is not None:
        if Message is not None:
            message_detail['message'] = Message
        else:
            pass
        if Subject is not None:
            if Subject != "":
                message_detail['message_subject'] = Subject
        else:
            pass    

        attachment_file = None
        attachment_file_name = None
        if 'attachment' in request.json:
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
        system_variable = mongo.db.mail_variables.find({})
        system_variable = [serialize_doc(doc) for doc in system_variable]
    
        missing_payload = []
        message_variables = []
        message = message_detail['message'].split('#')
        del message[0]
        rex = re.compile('!|@|\$|\%|\^|\&|\*|\:')
        for elem in message:
            varb = re.split(rex, elem)
            message_variables.append(varb[0])
        message_str = message_detail['message']
        for detail in message_variables:
            if detail in request.json['data']:
                if request.json['data'][detail] is not None:
                    rexWithString = '#' + re.escape(detail) + r'([!]|[@]|[\$]|[\%]|[\^]|[\&]|[\*]|[\:])'
                    message_str = re.sub(rexWithString, str(request.json['data'][detail]), message_str)
            else:
                for element in system_variable:
                    if "#" + detail == element['name'] and element['value'] is not None:
                        rexWithSystem = re.escape(element['name']) + r'([!]|[@]|[\$]|[\%]|[\^]|[\&]|[\*]|[\:])' 
                        message_str = re.sub(rexWithSystem, str(element['value']), message_str)    


        missing = message_str.split('#')
        del missing[0]
        missing_rex = re.compile('!|@|\$|\%|\^|\&|\*|\:')
        for elem in missing:
            missing_data = re.split(missing_rex, elem)
            missing_payload.append({"key": missing_data[0] , "type": "date" if missing_data[0] in dates_converter else "text"})
        
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
                if detail in request.json['data']:
                    if request.json['data'][detail] is not None:
                        rexWithString = '#' + re.escape(detail) + r'([!]|[@]|[\$]|[\%]|[\^]|[\&]|[\*]|[\:])'
                        mobile_message_str = re.sub(rexWithString, str(request.json['data'][detail]), mobile_message_str)
                else:
                    for element in system_variable:
                        if "#" + detail == element['name'] and element['value'] is not None:
                            rexWithSystem = re.escape(element['name']) + r'([!]|[@]|[\$]|[\%]|[\^]|[\&]|[\*]|[\:])' 
                            mobile_message_str = re.sub(rexWithSystem, str(element['value']), mobile_message_str)    

        subject_variables = []
        message_sub = message_detail['message_subject'].split('#')
        del message_sub[0]
        regex = re.compile('!|@|\$|\%|\^|\&|\*|\:')
        for elem in message_sub:
            sub_varb = re.split(regex, elem)
            subject_variables.append(sub_varb[0])
        message_subject = message_detail['message_subject']
        for detail in subject_variables:
            if detail in request.json['data']:
                if request.json['data'][detail] is not None:
                    rexWithString = '#' + re.escape(detail) + r'([!]|[@]|[\$]|[\%]|[\^]|[\&]|[\*]|[\:])'
                    message_subject = re.sub(rexWithString, str(request.json['data'][detail]), message_subject)

            else:
                for element in system_variable:
                    if "#" + detail == element['name'] and element['value'] is not None:
                        rexWithSystem = re.escape(element['name']) + r'([!]|[@]|[\$]|[\%]|[\^]|[\&]|[\*]|[\:])' 
                        message_subject = re.sub(rexWithSystem, str(element['value']), message_subject)  

        missing_subject = message_subject.split("#")
        del missing_subject[0]
        missing_sub_rex = re.compile('!|@|\$|\%|\^|\&|\*|\:')
        for elem in missing_subject:
            sub_varb_missing = re.split(missing_sub_rex, elem)
            missing_payload.append({"key": sub_varb_missing[0] , "type": "date" if sub_varb_missing[0] in dates_converter else "text"})

        if 'fromDate' in request.json['data'] and request.json['data']['fromDate'] is not None:
            if 'toDate' in request.json['data'] and request.json['data']['toDate'] is not None:
                if request.json['data']['fromDate'] == request.json['data']['toDate']:
                    message_str = message_str.replace(request.json['data']['fromDate'] + " to " + request.json['data']['toDate'],request.json['data']['fromDate'])

        if 'fromDate' in request.json['data'] and request.json['data']['fromDate'] is not None:
            if 'toDate' in request.json['data'] and request.json['data']['toDate'] is not None:
                if request.json['data']['fromDate'] == request.json['data']['toDate']:
                    message_subject = message_subject.replace(request.json['data']['fromDate'] + " to " + request.json['data']['toDate'],request.json['data']['fromDate'])

        phone_status = False
        phone_issue = False
        phone_issue_message = None
        if phone is not None:
            if app.config['ENV'] == 'development':
                phone =  "+918383871788"    #Phone number not should be hard coded
            try:
                if app.config['service'] == "textlocal":
                    req_sms = dispatch_sms(source="textlocal",apikey=app.config['localtextkey'],number=phone,message=mobile_message_str)
                    phone_status = req_sms
                elif app.config['service'] == "twilio":
                    req_sms = dispatch_sms(source="twilio",auth_token = app.config['twilioToken'],account_sid = app.config['twilioSid'],number=phone,message=mobile_message_str,from_v= app.config['twilio_number'])
                    phone_status = req_sms
            except Exception as e:
                phone_issue_message = repr(e)
                phone_status = False
                phone_issue = True

        
        download_pdf = "#letter_head #content #letter_foot"
        if header is not None:
            download_pdf = download_pdf.replace("#letter_head",header)
        else:
            download_pdf = download_pdf.replace("#letter_head",'')
        download_pdf = download_pdf.replace("#content",message_str)
        if footer is not None:
            download_pdf = download_pdf.replace("#letter_foot",footer)
        else:
            download_pdf = download_pdf.replace("#letter_foot",'')

        if message_detail['message_key'] == "Payslip":
            system_settings = mongo.db.system_settings.find_one({},{"_id":0})
            if system_settings is not None:
                if system_settings['pdf'] is True:
                    filename = "{}.pdf".format(str(uuid.uuid4()))
                    pdfkit = HTML(string=message_str).write_pdf(os.getcwd() + '/attached_documents/' + filename,stylesheets=[CSS(string='@page {size:Letter; margin: 0in 0in 0in 0in;}')])
                    attachment_file_name = filename
                    attachment_file = os.getcwd() + '/attached_documents/' + filename
                else:
                    pass
        if message_detail['message_key'] == "Interview Reminder":
            reminder_details = mongo.db.reminder_details.insert({
                'date': datetime.datetime.now(),
                'message_key': "Interview Reminder"
            })
        to = None
        bcc = None
        cc = None
        if app.config['ENV'] == 'development':
            if 'to' in request.json:
                for email in request.json.get('to'):
                    full_domain = re.search("@[\w.]+", email)  
                    domain = full_domain.group().split(".")
                    if domain[0] == "@excellencetechnologies":
                        to = [email]
                    else:
                        to = [app.config['to']]
            bcc = [app.config['bcc']]
            cc = [app.config['cc']]

        else:
            if app.config['ENV'] == 'production':
                if 'to' in request.json:
                    if not request.json['to']:
                        to = None
                    else:     
                        to = request.json['to']
                else:
                    to = None
                if 'bcc' in request.json:    
                    if not request.json['bcc']:
                        bcc = None
                    else:
                        bcc = request.json['bcc']
                else:
                    bcc = None
                
                if 'cc' in request.json: 
                    if not request.json['cc']:
                        cc = None
                    else:
                        cc = request.json['cc']
                else:        
                    cc = None            
        if message_detail['message_key'] == "interviewee_reject":
            reject_mail = None
            if app.config['ENV'] == 'production':
                if 'email' in request.json['data']:
                    reject_mail = request.json['data']['email']
                else:
                    return jsonify({"status": False,"Message": "No rejection mail is sended"}), 400
            else:
                if app.config['ENV'] == 'development':
                    email = request.json['data']['email']
                    full_domain = re.search("@[\w.]+", email)  
                    domain = full_domain.group().split(".")
                    if domain[0] == "@excellencetechnologies":
                        reject_mail = email
                    else:
                        reject_mail = app.config['to']   
            reject_handling = mongo.db.rejection_handling.insert_one({
            "email": reject_mail,
            'rejection_time': request.json['data']['rejection_time'],
            'send_status': False,
            'message': message_str,
            'subject': message_subject,
            'smtp_email': smtp_email
            }).inserted_id  
            return jsonify({"status":True,"*Note":"Added for Rejection"}),200   
        else:
            if to is not None:
                if smtp_email is not None:
                    mail_details = mongo.db.mail_settings.find_one({"mail_username":str(smtp_email),"origin": "RECRUIT"})
                    if mail_details is None:
                        return jsonify({"status":False,"Message": "Smtp not available in db"})
                    else:
                        send_email(message=message_str,recipients=to,subject=message_subject,bcc=bcc,cc=cc,filelink=attachment_file,filename=attachment_file_name,files=files,sending_mail=mail_details['mail_username'],sending_password=mail_details['mail_password'],sending_port=mail_details['mail_port'],sending_server=mail_details['mail_server'])
                        return jsonify({"status":True,"Subject":message_subject,"Message":download_pdf,"attachment_file_name":attachment_file_name,"attachment_file":attachment_file,"missing_payload":missing_payload,"phone_status" : phone_status, "phone_issue": phone_issue,"mobile_message": mobile_message_str}),200
                else:
                    send_email(message=message_str,recipients=to,subject=message_subject,bcc=bcc,cc=cc,filelink=attachment_file,filename=attachment_file_name,files=files)
                    return jsonify({"status":True,"Subject":message_subject,"Message":download_pdf,"attachment_file_name":attachment_file_name,"attachment_file":attachment_file,"missing_payload":missing_payload,"mobile_message": mobile_message_str,"phone_status" : phone_status, "phone_issue": phone_issue}),200
            else:
                return jsonify({"status":True,"*Note":"No mail will be sended!","Subject":message_subject,"Message":download_pdf,"attachment_file_name":attachment_file_name,"attachment_file":attachment_file,"missing_payload":missing_payload,"mobile_message": mobile_message_str, "phone_status" : phone_status, "phone_issue": phone_issue}),200
    else:
        return jsonify({"status":False ,"Message" : "Template not exist"})

@bp.route('/reminder_details', methods=["GET"])
def reminder_details():
    date = (datetime.datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')
    before_date = dateutil.parser.parse(date)
    details = mongo.db.reminder_details.aggregate([
        { '$match' : {
            'date': { '$gte' : before_date }
        }},
	{
        '$group' : {
            '_id' : {
                '$dateToString': { 'format': "%Y-%m-%d", 'date': "$date" }} , 'total' : { '$sum' : 1}
        }},
        { '$sort': { '_id': 1 } }
        ])
    details =[serialize_doc(doc) for doc in details]
    if (details):
        sum = 0
        if (len(details) > 1):
            sum += details[-1]['total'] + details[-2]['total'] 
        else :
            sum +=details[-1]['total']
        return jsonify ({'total': sum}), 200
    else:
        return jsonify ({'total': 0}), 200

@bp.route('/send_mail', methods=["POST"])
#@token.admin_required
def mails():
    if not request.json:
        abort(500) 
    MAIL_SEND_TO = None     
    phone = request.json.get("phone", None)
    if app.config['ENV'] == 'development':
        phone = "+918383871788"   #Phone number not should be hardcoded
        for email in request.json.get('to'):
            full_domain = re.search("@[\w.]+", email)  
            domain = full_domain.group().split(".")
            if domain[0] == "@excellencetechnologies":
                MAIL_SEND_TO = [email]
            else:
                MAIL_SEND_TO = [app.config['to']]
    else:
        if app.config['ENV'] == 'production':
            MAIL_SEND_TO = request.json.get("to",None)
    message = request.json.get("message",None)
    subject = request.json.get("subject",None)
    filename = request.json.get("filename",None)
    filelink = request.json.get("filelink",None)
    is_reminder = request.json.get("is_reminder",True)
    smtp_email = request.json.get("smtp_email",None)
    phone_message = request.json.get("phone_message",None)
    if not MAIL_SEND_TO and message:
        return jsonify({"status":False,"Message": "Invalid Request"}), 400
    bcc = None
    if 'bcc' in request.json:
        bcc = request.json['bcc']
    cc = None
    if 'cc' in request.json:
        cc = request.json['cc'] 
    if 'fcm_registration_id' in request.json:
        Push_notification(message=message,subject=subject,fcm_registration_id=request.json['fcm_registration_id'])
    phone_status = False
    phone_issue = False
    phone_issue_message = None
    if phone and phone_message is not None:
        try:
            if app.config['service'] == "textlocal":
                req_sms = dispatch_sms(source="textlocal",apikey=app.config['localtextkey'],number=phone,message=phone_message)
                phone_status = req_sms
            elif app.config['service'] == "twilio":
                req_sms = dispatch_sms(source="twilio",auth_token = app.config['twilioToken'],account_sid = app.config['twilioSid'],number=phone,message=phone_message,from_v= app.config['twilio_number'])
                phone_status = req_sms
        except Exception as e:
            phone_issue_message = repr(e)
            phone_status = False
            phone_issue = True

    if MAIL_SEND_TO is not None:
        for mail_store in MAIL_SEND_TO:
            id = mongo.db.recruit_mail.update({"message":message,"subject":subject,"to":mail_store},{
            "$set":{
                "phone":phone,
                "phone_message": phone_message,
                "phone_issue": phone_issue_message,
                "message": message,
                "subject": subject,
                "to":mail_store,
                "is_reminder":is_reminder,
                "date": datetime.datetime.now()
            }},upsert=True)
        if smtp_email is not None:
            mail_details = mongo.db.mail_settings.find_one({"mail_username":str(smtp_email),"origin": "RECRUIT"})
            if mail_details is None:
                return jsonify({"status":False,"Message": "Smtp not available in db"})
        else:
            mail_details = mongo.db.mail_settings.find_one({"origin": "RECRUIT","active": True})
            if mail_details is None:
                return jsonify({"status":False,"Message": "No smtp active in DB"})
        try:
            send_email(message=message,recipients=MAIL_SEND_TO,subject=subject,bcc=bcc,cc=cc,filelink=filelink,filename=filename,sending_mail=mail_details['mail_username'],sending_password=mail_details['mail_password'],sending_port=mail_details['mail_port'],sending_server=mail_details['mail_server'])   
            return jsonify({"status":True,"Message":"Sended","smtp":mail_details['mail_username'],"phone_status" : phone_status, "phone_issue": phone_issue}),200 
        except smtplib.SMTPServerDisconnected:
            return jsonify({"status":False,"Message": "Smtp server is disconnected"}), 400                
        except smtplib.SMTPConnectError:
            return jsonify({"status":False,"Message": "Smtp is unable to established"}), 400    
        except smtplib.SMTPAuthenticationError:
            return jsonify({"status":False,"Message": "Smtp login and password is wrong"}), 400                           
        except smtplib.SMTPDataError:
            return jsonify({"status":False,"Message": "Smtp account is not activated"}), 400 
        except Exception:
            return jsonify({"status":False,"Message": "Something went wrong with smtp"}), 400                                                         
    else:
        return jsonify({"status":False,"Message":"Please select a mail"}),400 

@bp.route('/email_template_requirement/<string:message_key>',methods=["GET", "POST"])
#@token.admin_required
def required_message(message_key):
    if request.method == "GET":
        ret = mongo.db.mail_template.find({"for": message_key},{"version":0,"version_details":0})
        if ret is not None:
            ret = [template_requirement(serialize_doc(doc)) for doc in ret]
            return jsonify(ret), 200
        else:
            return jsonify ({"message": "no template exist"}), 200    

@bp.route('/slack_test',methods=["POST"])
#@token.authentication
def token_test():
    email = request.json.get('email')
    try:
        slack = slack_id(email)
        slack_message(channel=[slack],message="Testing Slack Notification from HR System")
        return jsonify({"status":True,"message": "Slack Token Tested"}), 200
    except Exception:
        return jsonify({"status":False,"message": "Slack User not exist or invalid token"}), 400
        

@bp.route('/mail_test',methods=["POST"])
#@token.authentication
def mail_test():
    email = None
    if app.config['ENV']=='development':
        email = app.config['to']
    else:    
        email = request.json.get('email')
    try:
        send_email(message="SMTP WORKING!",recipients=[email],subject="SMTP TESTING MAIL!")
        return jsonify({"status":True,"message": "Smtp working"}), 200
    except smtplib.SMTPServerDisconnected:
        return jsonify({"status":False,"message": "Smtp server is disconnected"}), 400                
    except smtplib.SMTPConnectError:
        return jsonify({"status":False,"message": "Smtp is unable to established"}), 400    
    except smtplib.SMTPAuthenticationError:
        return jsonify({"status":False,"message": "Smtp login and password is wrong"}), 400                           
    except smtplib.SMTPDataError:
        return jsonify({"status":False,"message": "Smtp account is not activated"}), 400 
    except Exception:
        return jsonify({"status":False,"message": "Something went wrong with smtp"}), 400                                                         
