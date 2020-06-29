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
from app.modules.phone_util import create_sms,Push_notification
from app.modules.template_util import assign_letter_heads, construct_template, attach_letter_head,generate_full_template_from_string_payload
from app.modules.sendmail_util import create_sender_list
bp = Blueprint('notify', __name__, url_prefix='/notify')
        

#dispatch was made to send particular message on slack but those message can be sended on email too
@bp.route('/dispatch', methods=["POST"])
#@token.authentication
def construct_dispatch_notification():
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



#preview is used in recruit and hr to generate message for the templates and can also be used to send email if details are provided
@bp.route('/preview', methods=["POST"])
#@token.admin_required
#@token.authentication
def send_mails():
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
    smtp_email = request.json.get("smtp_email",None)
    phone = request.json.get("phone", None)

    message_detail = mongo.db.mail_template.find_one({"message_key": MSG_KEY})
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
            letter_heads_response = assign_letter_heads(message_detail['template_head'])
            header = letter_heads_response.get('header')
            footer = letter_heads_response.get('footer')

        
        message = None
        subject = None
        mobile_message_str = None
        #payload going = {"req_message":"message string","request":"data variable","message_detail":"mail template"}
        missing_payload = generate_full_template_from_string_payload(req_message= message_detail['message'], request= request.json['data'] , message_detail=message_detail)

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
            phone_sms_about = create_sms( phone= phone, mobile_message_str= mobile_message_str )
            phone_status = phone_sms_about.get('phone_status')
            phone_issue = phone_sms_about.get('phone_issue')
            phone_issue_message = phone_sms_about.get('phone_issue_message')

        attachtment_about = attach_letter_head(header=header, footer= footer, message= message)
        message = attachtment_about.get('message')
        #testing

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
            sending_message_details = {
                "smtp_email": smtp_email,
                "message": message_str,
                "subject": message_subject,
                "files": files,
                "single_filelink": attachment_file,
                "single_filename": attachment_file_name
            }
            try:
                sender_details = create_sender_list(request= request.json, details= sending_message_details)
                if 'mailing_staus' in sender_details:
                    return jsonify({ 
                        "status": True,
                        "*Note": "No mail will be sended!",
                        "Subject": message_subject,
                        "Message": message_str,
                        "attachment_file_name": attachment_file_name,
                        "attachment_file": attachment_file,
                        "missing_payload": missing_payload,
                        "mobile_message": mobile_message_str,
                        "phone_status": phone_status,
                        "phone_issue": phone_issue
                    }), 200
                else:
                    return jsonify({ 
                        "status":True,
                        "Subject": message_subject,
                        "Message": message_str,
                        "attachment_file_name":attachment_file_name,
                        "attachment_file":attachment_file,
                        "missing_payload":missing_payload,
                        "mobile_message": mobile_message_str,
                        "phone_status" : phone_status, 
                        "phone_issue": phone_issue
                        }),200
            except Exception as error:
                return jsonify({"status": False, "Message": str(error)})
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
    if app.config['ENV'] == 'development':
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
    phone = request.json.get("phone", None)
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
