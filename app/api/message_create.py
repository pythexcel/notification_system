from app import mongo
from flask import (Blueprint, flash, jsonify, abort, request)
from app.util import serialize_doc,template_requirement
import datetime
from bson.objectid import ObjectId

bp = Blueprint('notification_message', __name__, url_prefix='/message')

@bp.route('/configuration/<string:message_origin>', methods=["GET", "PUT"])
def notification_message(message_origin):
    if request.method == "GET":
        ret = mongo.db.notification_msg.find({"message_origin":message_origin})
        ret = [serialize_doc(doc) for doc in ret]
        return jsonify(ret)
    if request.method == "PUT":
        MSG = request.json.get("message", None)
        MSG_KEY = request.json.get("message_key", None)
        MSG_TYPE = request.json.get("message_type", None)
        MSG_Color = request.json.get("message_color", None)
        Working = request.json.get("working", True)
        slack_channel = request.json.get("slack_channel",None)
        email_group = request.json.get("email_group",None)
        channel = request.json.get("channels",None)
        sended_to = request.json.get("sended_to",None)
        # Have added this for_email etc so have better control over single messages that if want to send on particular platform or not 
        for_email = request.json.get("for_email",False)
        for_slack = request.json.get("for_slack",False)
        for_phone = request.json.get("for_phone",False)

        if not MSG and MSG_TYPE and MSG_KEY:
            return jsonify({"msg": "Invalid Request"}), 400

        ret = mongo.db.notification_msg.update({"message_key": MSG_KEY}, {
           "$set": {
                "message": MSG,
                "message_key": MSG_KEY,
                "message_origin": message_origin,
                "message_type": MSG_TYPE,
                "sended_to": sended_to,
                "working":Working,
                "message_color": MSG_Color,
                "slack_channel":slack_channel,
                "email_group":email_group,
                "channels":channel,
                "for_email": for_email,
                "for_slack": for_slack,
                "for_phone": for_phone
            }
        },upsert=True)
        return jsonify(str(ret))

# This api was maded bcoz HR have some predefined variables which now i am storing in this system with their value and name
@bp.route('/special_variable', methods=["GET","PUT"])
def special_var():
    if request.method == "GET":
        ret = mongo.db.mail_variables.find({})
        ret = [serialize_doc(doc) for doc in ret]
        return jsonify(ret)
    if request.method == "PUT":
        name = request.json.get("name", None)
        value = request.json.get("value", None)
        variable_type = request.json.get("variable_type", None)
        ret = mongo.db.mail_variables.update({"name":name},{
           "$set": {
                "name": name,
                "value": value,
                "variable_type":variable_type
            }
        },upsert=True)
        return jsonify(str(ret))        

# This will return  and add all the mail templates and which are required from HR 
@bp.route('/get_email_template/<string:message_origin>', methods=["GET", "PUT"])
def mail_message(message_origin):
    if request.method == "GET":
        ret = mongo.db.mail_template.find({"message_origin":message_origin})
        ret = [special(serialize_doc(doc)) for doc in ret]
        return jsonify(ret)
    if request.method == "PUT":
        MSG = request.json.get("message", None)
        MSG_KEY = request.json.get("message_key", None)
        Working = request.json.get("working", True)
        MSG_SUBJECT = request.json.get("message_subject",None)
        if not MSG and MSG_KEY and message_origin and MSG_SUBJECT:
            return jsonify({"MSG": "Invalid Request"}), 400
        ver = mongo.db.mail_template.find_one({"message_key": MSG_KEY})
        if ver is not None:
            version =  ver['version'] + 1
            ver_message = ver['message']
            ret = mongo.db.mail_template.update({"message_key": MSG_KEY}, 
                {
                "$push": {
                    "version_details": {
                        "message":ver_message,
                        "version": ver['version']
                        }
                },
                "$set": {
                    "message": MSG,
                    "message_key": MSG_KEY,
                    "working":Working,
                    "message_origin":message_origin,
                    "message_subject":MSG_SUBJECT,
                    "version": version
                }
                })
            return jsonify({"MSG":"Template Updated"}), 200        
        else:
            ret = mongo.db.mail_template.update({"message_key": MSG_KEY}, {
                "$set": {
                    "message": MSG,
                    "message_key": MSG_KEY,
                    "working":Working,
                    "message_origin":message_origin,
                    "message_subject":MSG_SUBJECT,
                    "version": 1
                }
            })
            return jsonify({"MSG":"Template Added"}), 200

@bp.route('/letter_heads', methods=["GET","PUT"])
def letter_heads():
    if request.method == "GET":
        ret = mongo.db.letter_heads.find({})
        ret = [serialize_doc(doc) for doc in ret]
        return jsonify(ret)
    if request.method == "PUT":
        name = request.json.get("name", None)
        header_value = request.json.get("header_value", None)
        footer_value = request.json.get("footer_value", None)
        Working = request.json.get("working", True)
        ret = mongo.db.letter_heads.update({"name":name},{
           "$set": {
                "name": name,
                "header_value": header_value,
                "footer_value": footer_value,
                "working": Working 
            }
        },upsert=True)
        return jsonify({"MSG":"Letter Head Created"}), 200  

@bp.route('/assign_letter_heads/<string:template_id>/<string:letter_head_id>', methods=["PUT"])
def assign_letter_heads(template_id,letter_head_id):    
    ret = mongo.db.mail_template.update({"_id":ObjectId(template_id)},{
        "$set": {
            "template_head": letter_head_id  
        }
    })
    return jsonify({"MSG":"Letter Head Added To Template"}), 200  