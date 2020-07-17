from app.auth import token
from app import mongo
from flask import (Blueprint, flash, jsonify, abort, request,url_for,send_from_directory)
from app.email.model.sendmail import send_email
from app.util.serializer import serialize_doc 
from app.email.model.template_making import template_requirement
from app.slack.model.validate_message import validate_message
from app.config import message_needs,dates_converter
from app.slack.model.slack_util import slack_message,slack_id
from app.phone.util.phone import dispatch_sms,create_sms
from app.push_notification.util.push_notification import Push_notification
from flask_jwt_extended import (JWTManager, jwt_required, create_access_token,
                                get_jwt_identity, get_current_user,
                                jwt_refresh_token_required,
                                verify_jwt_in_request)
import json
import uuid
import os 
from weasyprint import HTML, CSS
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
from app.email.util.template_util import generate_full_template_from_string_payload,fetch_msg_and_subject_by_date
from app.email.model.template_making import fetch_recipients_by_mode
from app.email.model.recruit_mail import update_recruit_mail_msg
from app.slack.model.construct_payload import contruct_payload_from_request
from app.model.interview_reminders import fetch_interview_reminders
from app.email.util.template_util import attach_letter_head
from app.email.model.template_making import construct_attachments_in_by_msg_details
from app.email.util.get_recipients import get_recipients_from_request
from app.slack.model.notification_msg import get_notification_function_by_key
from app.email.util.date_convertor import convert_dates_to_format
from app.email.model.interview_rejection import interview_rejection

bp = Blueprint('email_preview', __name__, url_prefix='/notify')


#1preview is used in recruit and hr to generate message for the templates and can also be used to send email if details are provided
@bp.route('/preview', methods=["POST"])
#@token.admin_required
#@token.authentication
def send_or_preview_mail():
    if not request.json:
        abort(500)
    req = request.json
    try:
        req = convert_dates_to_format(dates_converter=dates_converter,req=req) #Calling function for date convertor which will return modified json

        MSG_KEY = req.get("message_key", None)  
        Data = req.get("data",None)
        Message = req.get("message",None)
        Subject = req.get("subject",None)
        smtp_email = req.get("smtp_email",None)
        phone = req.get("phone", None)

        message_detail = mongo.db.mail_template.find_one({"message_key": MSG_KEY}) #calling function for message details by message key

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

            system_variable = mongo.db.mail_variables.find({})
            system_variable = [serialize_doc(doc) for doc in system_variable]

            #here calling function for filter attachments,header,footer etc details from message details
            attachment_file,attachment_file_name,files,header,footer = construct_attachments_in_by_msg_details(message_detail=message_detail,req=req)
            
            #Here calling function for filter message,mobile message,subject and any missing payload value
            message_str,message_subject,mobile_message_str,missing_payload = generate_full_template_from_string_payload(message_detail= message_detail, request= req,system_variable=system_variable)
            
            #here calling function for filter out message and subject using date if available else will return existing message and subject from up
            message_str,message_subject = fetch_msg_and_subject_by_date(request=req,message_str=message_str,message_subject=message_subject)

            phone_status = False
            phone_issue = False
            phone_issue_message = None
            #Here calling function for phone status info etc if phone available 
            if phone is not None:
                phone_status,phone_issue,phone_issue_message = create_sms( phone= phone, mobile_message_str= mobile_message_str )

            #function calling for create message with header footer
        
            download_pdf = attach_letter_head(header=header, footer= footer, message= message_str)
    except Exception as error:
        return(str(error)),400

    else:
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
        to,bcc,cc = get_recipients_from_request(req)
        if message_detail['message_key'] == "interviewee_reject":
            interview_rejection(req,message_str,message_subject,smtp_email)
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


#Api for send mail
@bp.route('/send_mail', methods=["POST"])
#@token.admin_required
def mails():
    if not request.json:
        abort(500) 
    #Here calling function for fetch recipients according to env 
    # if env is developemet will return only excellence mails
    #else return acurate requested to mail
    try:
        MAIL_SEND_TO = fetch_recipients_by_mode(request=request.json)
    except Exception as error:
        return(str(error)),400

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

    #here calling same existing function which called before in preview api for phone message status
    phone_status = False
    phone_issue = False
    phone_issue_message = None
    if phone and phone_message is not None:
        phone_status,phone_issue,phone_issue_message = create_sms( phone= phone, mobile_message_str= phone_message )


    if MAIL_SEND_TO is not None:
        for mail_store in MAIL_SEND_TO:
            #Here calling function for update recruit mails into a collection
            try:
                update_recruit_mail_msg(phone=phone,phone_message=phone_message,phone_issue=phone_issue,message=message,subject=subject,to=mail_store,is_reminder=is_reminder)
            except Exception as error:
                return(str(error)),400

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


#Api for return email template by message key
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


#Api for test mailing service is working or not
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

