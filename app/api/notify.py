from app import token
from app import mongo
from flask import (Blueprint, flash, jsonify, abort, request)
from app.mail_util import send_email
from app.util import serialize_doc,construct_message,validate_message
from app.config import message_needs,messages,config_info
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

# Below the Api is for generating the pdf from mail template and also currently the same api will send the mail of that pdf content if sending credintials are avialable

# REASON FOR CURRENTLY ONE API FOR BOTH IS ARUN SIR ASKED THAT FOR CURRENT SCENARIO LET IT BE ONE API
@bp.route('/preview', methods=["POST"])
def send_mails():
    if not request.json:
        abort(500)
    MSG_KEY = request.json.get("message_key", None)  
    Data = request.json.get("data",None)
    message_detail = mongo.db.mail_template.find_one({"message_key": MSG_KEY})
    # Below the same functionality is followed of replacing the variables with the data sended and in request also it will replace the value if it is not send in request but it is in special variable collection 
    if message_detail is not None: 
        ret = mongo.db.mail_variables.find({})
        ret = [serialize_doc(doc) for doc in ret] 
        message_variables = []
        message = message_detail['message'].split()
        for elem in message:
            if elem[0]=='#':
                message_variables.append(elem[1:])        
        message_str = message_detail['message']
        for detail in message_variables:
            if detail in request.json:    
                message_str = message_str.replace("#"+detail, request.json[detail])
            else:
                if detail in request.json['data']:
                    message_str = message_str.replace("#"+detail, request.json['data'][detail])
                else:
                    for element in ret:
                        if "#" + detail == element['name'] and element['value'] is not None:
                            message_str = message_str.replace("#"+detail, element['value'])  
        # Here below i am generating a pdf from the above string for pdf generation and storing in cloudnary
        filename = str(uuid.uuid4())+'.pdf'
        # Here below the reason for writing css here for this library is else the pdf is not getting formated properly
        pdfkit = HTML(string=message_str).write_pdf(filename,stylesheets=[CSS(string='@page {size:Letter; margin: 0in 0in 0in 0in;}')])
        file = cloudinary.uploader.upload(filename)
        # here after generating of cloudnary link of pdf removing it from local storage
        os.remove(filename)
        if 'to' in request.json:
            # here if mail credintials are provdied below will work
            # as usual replacing the header , footer and page break value so they will not be sended in mail
            for elem in ret:
                if elem['name'] == "#page_header":
                    head = elem['value']
                if elem['name'] == "#page_footer":
                    foo = elem['value']
                if elem['name'] == "#page_break":
                    br = elem['value']                    
                    message_str = message_str.replace(head,'')
                    message_str = message_str.replace(foo,'')
                    message_str = message_str.replace(br,'')
            # condition for bcc and cc if present in request.json
            bcc = None
            if 'bcc' in request.json:
                bcc = request.json['bcc']
            cc = None
            if 'cc' in request.json:
                cc = request.json['cc']
            send_email(message=message_str,recipients=request.json['to'],subject=message_detail['message_subject'],bcc=bcc,cc=cc)
        return jsonify({"status":True,"Message":message_str,"pdf": file['url']}),200
        