from app import mongo
from flask import (Blueprint, flash, jsonify, abort, request)
from app.util import serialize_doc,special
import datetime

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
@bp.route('/get_email_template', methods=["GET", "PUT"])
def mail_message():
    if request.method == "GET":
        ret = mongo.db.mail_template.find({})
        #Below the function special will return all the varibles of each particular template required 
        ret = [special(serialize_doc(doc)) for doc in ret]
        return jsonify(ret)
    if request.method == "PUT":
        MSG = request.json.get("message", None)
        
        MSG_KEY = request.json.get("message_key", None)
        Working = request.json.get("working", True)
        MSG_SUBJECT = request.json.get("message_subject",None)
        if not MSG and MSG_KEY:
            return jsonify({"msg": "Invalid Request"}), 400
        ret = mongo.db.mail_template.update({"message_key": MSG_KEY}, {
           "$set": {
                "message": MSG,
                "message_key": MSG_KEY,
                "working":Working,
                "message_subject":MSG_SUBJECT
            }
        },upsert=True)
        return jsonify(str(ret))        