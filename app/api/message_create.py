import os
import uuid
from app import mongo
from app import token
from flask import (Blueprint, flash, jsonify, abort, request)
from app.util import serialize_doc, template_requirement,allowed_file
import datetime
from bson.objectid import ObjectId
from flask_jwt_extended import (JWTManager, jwt_required, create_access_token,
                                get_jwt_identity, get_current_user,
                                jwt_refresh_token_required,
                                verify_jwt_in_request)
from werkzeug.utils import secure_filename
from flask import current_app as app
from app.slack_util import slack_message


bp = Blueprint('notification_message', __name__, url_prefix='/message')


@bp.route('/configuration/<string:message_origin>', methods=["GET", "PUT"])
#@token.admin_required
def notification_message(message_origin):
    if request.method == "GET":
        ret = mongo.db.notification_msg.find(
            {"message_origin": message_origin})
        ret = [serialize_doc(doc) for doc in ret]
        return jsonify(ret)
    if request.method == "PUT":
        MSG = request.json.get("message", None)
        MSG_KEY = request.json.get("message_key", None)
        MSG_TYPE = request.json.get("message_type", None)
        MSG_Color = request.json.get("message_color", None)
        Working = request.json.get("working", True)
        submission_type = request.json.get("submission_type", None)
        slack_channel = request.json.get("slack_channel", None)
        email_group = request.json.get("email_group", None)
        channel = request.json.get("channels", None)
        sended_to = request.json.get("sended_to", None)
        for_email = request.json.get("for_email", False)
        for_slack = request.json.get("for_slack", False)
        for_phone = request.json.get("for_phone", False)

        if not MSG and MSG_TYPE and MSG_KEY:
            return jsonify({"message": "Invalid Request"}), 400

        ret = mongo.db.notification_msg.update({"message_key": MSG_KEY}, {
            "$set": {
                "message": MSG,
                "message_key": MSG_KEY,
                "message_origin": message_origin,
                "message_type": MSG_TYPE,
                "sended_to": sended_to,
                "submission_type": submission_type,
                "working": Working,
                "message_color": MSG_Color,
                "slack_channel": slack_channel,
                "email_group": email_group,
                "channels": channel,
                "for_email": for_email,
                "for_slack": for_slack,
                "for_phone": for_phone
            }
        },upsert=True)
        return jsonify({"message": "upsert"}), 200


@bp.route('/special_variable', methods=["GET", "PUT"])
#@token.authentication
#@token.admin_required
def special_var():
    if request.method == "GET":
        ret = mongo.db.mail_variables.find({})
        ret = [serialize_doc(doc) for doc in ret]
        return jsonify(ret)
    if request.method == "PUT":
        name = request.json.get("name", None)
        value = request.json.get("value", None)
        variable_type = request.json.get("variable_type", None)
        ret = mongo.db.mail_variables.update({"name": name}, {
            "$set": {
                "name": name,
                "value": value,
                "variable_type": variable_type
            }
        },upsert=True)
        return jsonify({"message": "upsert"}), 200


@bp.route('/get_email_template/<string:message_origin>',methods=["GET", "PUT","DELETE"])
#@token.admin_required
def mail_message(message_origin):
    if request.method == "GET":
        ret = mongo.db.mail_template.find({"message_origin": message_origin})
        ret = [template_requirement(serialize_doc(doc)) for doc in ret]
        return jsonify(ret), 200
    if request.method == "DELETE":
        MSG_KEY = request.json.get("message_key", None)
        ret = mongo.db.mail_template.remove({"message_key": MSG_KEY})
        return jsonify({
                "message": "Template Deleted",
                "status": True
            }), 200
    if request.method == "PUT":
        MSG = request.form["message"]
        MSG_KEY = request.form["message_key"]
        mobile_message = request.form["mobile_message"]
        working = True
        if "working" in request.form:
            working = request.form["working"]
        MSG_SUBJECT = request.form["message_subject"]
        for_detail = None
        if 'for_detail' in request.form:
            for_detail = request.form["for_detail"]
        recruit_details = None
        if 'recruit_details' in request.form:
            recruit_details = request.form["recruit_details"]
        Doc_type = request.form["doc_type"]
        default = False
        if "default" in request.form:
            default = True
            
        if not MSG and MSG_KEY and message_origin and MSG_SUBJECT:
            return jsonify({"MSG": "Invalid Request"}), 400
        
        ver = mongo.db.mail_template.find_one({"message_key": MSG_KEY})
        if ver is not None:
                 
            version = ver['version'] + 1
            ver_message = ver['message']
            ret = mongo.db.mail_template.update({"message_key": MSG_KEY}, {
                "$push": {
                    "version_details": {
                        "message": ver_message,
                        "version": ver['version']
                    }
                },
                "$set": {
                    "message": MSG,
                    "message_key": MSG_KEY,
                    "working": working,
                    "mobile_message" : mobile_message,
                    "message_origin": message_origin,
                    "message_subject": MSG_SUBJECT,
                    "version": version,
                    "for": for_detail,
                    "default": default,
                    "recruit_details":recruit_details,
                    "Doc_type": Doc_type
                }
            })
            if 'num_attachment' in request.form:
                if request.form['num_attachment'] != 0:
                    for i in range(0,int(request.form['num_attachment'])):
                        file = request.files['attachment_file_{}'.format(i)]
                        if file and allowed_file(file.filename):
                            filename = secure_filename(file.filename)
                            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))    
                            attachment_file = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                            attachment_file_name = filename
                            mongo.db.mail_template.update({"message_key": MSG_KEY},{
                            "$push": {
                                "attachment_files":{
                                    "file_id": str(uuid.uuid4()),
                                    "file_name": attachment_file_name,
                                    "file": attachment_file
                                }
                                }
                            })
            else:
                pass

            return jsonify({
                "message": "Template Updated",
                "status": True
            }), 200
        
        else:
            ret = mongo.db.mail_template.insert_one({
                "message": MSG,
                "message_key": MSG_KEY,
                "working": working,
                "mobile_message" : mobile_message,
                "message_origin": message_origin,
                "message_subject": MSG_SUBJECT,
                "version": 1,
                "default": False,
                "for": for_detail,
                "recruit_details":recruit_details,
                "Doc_type": Doc_type, 
            }).inserted_id

            if 'num_attachment' in request.form:
                if request.form['num_attachment'] != 0:
                    for i in range(0,int(request.form['num_attachment'])):
                        file = request.files['attachment_file_{}'.format(i)]
                        if file and allowed_file(file.filename):
                            filename = secure_filename(file.filename)
                            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))    
                            attachment_file = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                            attachment_file_name = filename
                            mongo.db.mail_template.update({"message_key": MSG_KEY},{
                            "$push": {
                                "attachment_files":{
                                    "file_id": str(uuid.uuid4()),
                                    "file_name": attachment_file_name,
                                    "file": attachment_file
                                }
                                }
                            })
            else:
                pass
                                
            return jsonify({"message": "Template Added", "status": True}), 200

@bp.route('/delete_file/<string:id>/<string:file_id>',methods=["DELETE"])
#@token.admin_required
def delete_attached_file(id,file_id):
    ret = mongo.db.mail_template.update({"_id": ObjectId(id)},{
        "$pull": {
            "attachment_files":{
                "file_id": file_id

            } 
        }
        })
    return jsonify({"message": "File deleted", "status": True}), 200


@bp.route('/letter_heads', methods=["GET", "PUT"])
@bp.route('/letter_heads/<string:id>', methods=["DELETE"])
#@token.admin_required
def letter_heads(id=None):
    if request.method == "GET":
        ret = mongo.db.letter_heads.find({})
        ret = [serialize_doc(doc) for doc in ret]
        return jsonify(ret), 200
    if request.method == "PUT":
        name = request.json.get("name", None)
        header_value = request.json.get("header_value", None)
        footer_value = request.json.get("footer_value", None)
        Working = request.json.get("working", True)
        ret = mongo.db.letter_heads.update({"name": name}, {
            "$set": {
                "name": name,
                "header_value": header_value,
                "footer_value": footer_value,
                "working": Working
            }
        },upsert=True)
        return jsonify({"message": "Letter Head Created","status":True}), 200
    if request.method == "DELETE":
        ret = mongo.db.letter_heads.remove({"_id": ObjectId(id)})
        return jsonify({"message": "Letter Head Deleted","status":True}), 200


@bp.route('/assign_letter_heads/<string:template_id>/<string:letter_head_id>',methods=["PUT"])
#@token.admin_required
def assign_letter_heads(template_id, letter_head_id):
    ret = mongo.db.mail_template.update(
        {"_id": ObjectId(template_id)},
        {"$set": {
            "template_head": letter_head_id
        }})
    return jsonify({"message": "Letter Head Added To Template"}), 200

@bp.route('/slack_channel_test', methods=["POST"])
#@token.admin_required
def slack_channel_test():
    channel = request.json.get("channel")
    ret = mongo.db.working_channels.insert_one({
        "channel_id" : channel,
    })
    slack_message(channel=[channel],message="Your slack account is integrated")
    return jsonify({"message": "Sended","status":True}), 200

@bp.route('/triggers',methods=["GET"])
#@token.admin_required
def get_triggers():
    duplicate = []
    triggers = []

    ret = mongo.db.mail_template.find({"message_origin": "RECRUIT"})
    ret = [serialize_doc(doc) for doc in ret]
    if ret:
        for data in ret:
            duplicate.append(data['for'])
    for elem in duplicate:
        if elem not in triggers:
            triggers.append(elem)
    return jsonify({"triggers": triggers}), 200
