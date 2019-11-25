from app import token
from app import mongo
from flask import (Blueprint, flash, jsonify, abort, request,url_for,send_from_directory)
from app.mail_util import send_email
from app.util import serialize_doc,construct_message,validate_message,allowed_file,template_requirement
from app.config import message_needs,messages,config_info,Base_url
from app.slack_util import slack_message 
from flask_jwt_extended import (JWTManager, jwt_required, create_access_token,
                                get_jwt_identity, get_current_user,
                                jwt_refresh_token_required,
                                verify_jwt_in_request)
import json
import cloudinary
import cloudinary.uploader
import cloudinary.api
from weasyprint import HTML, CSS
import uuid
import os 
from app.phone_util import Push_notification
from bson.objectid import ObjectId
from werkzeug import secure_filename
from flask import current_app as app
import re
import base64
import bson


bp = Blueprint('notify', __name__, url_prefix='/notify')


@bp.route('/dispatch', methods=["POST"])
def dispatch():
    if not request.json:
        abort(500)
    MSG_KEY = request.json.get("message_key", None)  #salary slip,xyz
    missed_req = {}
    message_detail = mongo.db.notification_msg.find_one({"message_key": MSG_KEY})
    # finding data of payload from request key via json
    for data in messages:
        if data['message_key'] == MSG_KEY:
            missed_req = data
    # below will checki if message detail is completely empty return data from json or else if its any value is none replace it from json data
    if message_detail is not None:
        update = message_detail.update((k,v) for k,v in missed_req.items() if v is None)
    else:
        message_detail = missed_req
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
# @token.admin_required
def send_mails():
    if not request.json:
        abort(500)
    MSG_KEY = request.json.get("message_key", None)  
    Data = request.json.get("data",None)
    file = request.files.getlist("files")
    message_detail = mongo.db.mail_template.find_one({"message_key": MSG_KEY})
    if message_detail is not None: 
        filelink = None
        if 'filelink' in message_detail:
            filelink = message_detail['filelink']
        filename = None
        if 'filename' in message_detail:
            filename = message_detail['filename']    
        # var = mongo.db.letter_heads.find_one({"_id":ObjectId(message_detail['template_head'])})
        # header = None
        # footer = None
        # if var is not None:
            # header = var['header_value']
            # footer = var['footer_value']
        system_variable = mongo.db.mail_variables.find({})
        system_variable = [serialize_doc(doc) for doc in system_variable]
        message_variables = []
        message = message_detail['message'].split('#')
        del message[0]
        rex = re.compile('!|@|\$|\%|\^|\&|\*|\:|\;')
        for elem in message:
            varb = re.split(rex, elem)
            message_variables.append(varb[0])
        message_str = message_detail['message']
        for detail in message_variables:
            if detail in request.json['data']:
                rexWithString = '#' + re.escape(detail) + r'([!]|[@]|[\$]|[\%]|[\^]|[\&]|[\*]|[\:]|[\;])'
                message_str = re.sub(rexWithString, request.json['data'][detail], message_str)
            else:
                # HERE! NEED TO WRITE CONDITION FOR HEADER/FOOTER REPLACE WITH RE WHEN LETTER HEADS ARE ASSIGNED
                # if header is not None:
                    # message_str = message_str.replace("#page_header",header)
                # if footer is not None:
                    # message_str = message_str.replace("#page_footer",footer)
                for element in system_variable:
                    if "#" + detail == element['name'] and element['value'] is not None:
                        rexWithSystem = re.escape(element['name']) + r'([!]|[@]|[\$]|[\%]|[\^]|[\&]|[\*]|[\:]|[\;])' 
                        message_str = re.sub(rexWithSystem, element['value'], message_str)                     


        subject_variables = []
        message_sub = message_detail['message_subject'].split('#')
        del message[0]
        regex = re.compile('!|@|\$|\%|\^|\&|\*|\:|\;')
        for elem in message_sub:
            sub_varb = re.split(regex, elem)
            subject_variables.append(sub_varb[0])
        message_subject = message_detail['message_subject']
        for detail in subject_variables:
            if detail in request.json['data']:
                rexWithString = '#' + re.escape(detail) + r'([!]|[@]|[\$]|[\%]|[\^]|[\&]|[\*]|[\:]|[\;])'
                message_subject = re.sub(rexWithString, request.json['data'][detail], message_subject)
            else:
                for element in system_variable:
                    if "#" + detail == element['name'] and element['value'] is not None:
                        rexWithSystem = re.escape(element['name']) + r'([!]|[@]|[\$]|[\%]|[\^]|[\&]|[\*]|[\:]|[\;])' 
                        message_subject = re.sub(rexWithSystem, element['value'], message_subject)                     
        filename = str(uuid.uuid4())+'.pdf'
        link = None
        if 'pdf' in request.json and request.json['pdf'] is True:
            pdfkit = HTML(string=message_str).write_pdf(os.getcwd() + '/attached_documents/' + filename,stylesheets=[CSS(string='@page {size:Letter; margin: 0in 0in 0in 0in;}')])
            # pdfkit = HTML(string=message_str).write_pdf(filename,stylesheets=[CSS(string='@page {size:Letter; margin: 0in 0in 0in 0in;}')])
            try:
                file = cloudinary.uploader.upload(os.getcwd() + '/attached_documents/' + filename)
                # file = cloudinary.uploader.upload(filename)
                link = file['url']
            except ValueError:
                link = Base_url + "/attached_documents/" + filename
        
        # USE NAHI YAAD H NEECHE CODE KA        
        # filelink = None
        # if 'pdf' in request.json and request.json['pdf'] is True:
        #     # for local attachment cloudnary link won't work
        #     # filelink = os.getcwd() + '/pdf/' + filename
        #     filelink = filename
        
        for elem in system_variable:
            if elem['name'] == "#page_header":
                head = elem['value']
            if elem['name'] == "#page_footer":
                foo = elem['value']
            if elem['name'] == "#page_break":
                br = elem['value']                    
                message_str = message_str.replace(head,'')
                message_str = message_str.replace(foo,'')
                message_str = message_str.replace(br,'') 
        # if header is not None:
        #     message_str = message_str.replace(header,'')
        # if footer is not None:
        #     message_str = message_str.replace(footer,'')
        if message_detail['message_key'] == "interviewee_reject":
            reject_handling = mongo.db.rejection_handling.insert_one({
            "email": request.json['data']['email'],
            'rejection_time': request.json['data']['rejection_time'],
            'send_status': False,
            'message': message_str,
            'subject': message_subject
            }).inserted_id    
        else:
            pass
        if 'pdf' in request.json and request.json['pdf'] is True:
            return jsonify({"status":True,"Subject":message_subject,"Message":message_str,"pdf": link,"filename":filename,"filelink":filelink}),200
        else:
            return jsonify({"status":True,"Subject":message_subject,"Message":message_str,"filename":filename,"filelink":filelink}),200

            
@bp.route('/send_mail', methods=["POST"])
# @token.admin_required
def mails():
    if not request.json:
        abort(500)  
    MAIL_SEND_TO = ["recruit_testing@mailinator.com"]
    # MAIL_SEND_TO = request.json.get("to",None)
    message = request.json.get("message",None)
    subject = request.json.get("subject",None)
    filename = request.json.get("filename",None)
    filelink = request.json.get("filelink",None)
    print(filename,filelink)
    if not MAIL_SEND_TO and message:
        return jsonify({"MSG": "Invalid Request"}), 400
    bcc = None
    if 'bcc' in request.json:
        bcc = request.json['bcc']
    cc = None
    if 'cc' in request.json:
        cc = request.json['cc']   
    send_email(message=message,recipients=MAIL_SEND_TO,subject=subject,bcc=bcc,cc=cc,filelink=filelink,filename=filename)    
    if 'fcm_registration_id' in request.json:
        Push_notification(message=message,subject=subject,fcm_registration_id=request.json['fcm_registration_id'])
    return jsonify({"status":True,"Message":"Sended"}),200 


@bp.route('/email_template_requirement/<string:message_key>',methods=["GET", "POST"])
@token.admin_required
def required_message(message_key):
    if request.method == "GET":
        ret = mongo.db.mail_template.find({"for": message_key},{"version":0,"version_details":0})
        if ret is not None:
            ret = [template_requirement(serialize_doc(doc)) for doc in ret]
            return jsonify(ret), 200
        else:
            return jsonify ({"Message": "no template exist"}), 200    
