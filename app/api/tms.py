from app import token
from app import mongo
from flask import (Blueprint, flash, jsonify, abort, request)
import dateutil.parser
from bson.objectid import ObjectId
from slackclient import SlackClient
import requests
import datetime
from app.config import simple_message_needs, Notification_message_needs,Mail_update_needs
from app.slack_util import slack_msg, slack_message, serialize_doc, slack_attach,notifie_user
from flask_jwt_extended import (JWTManager, jwt_required, create_access_token,
                                get_jwt_identity, get_current_user,
                                jwt_refresh_token_required,
                                verify_jwt_in_request)

bp = Blueprint('tms', __name__, url_prefix='/tms')


@bp.route('/dispatch_notification', methods=["POST"])
def dispatch():
    if not request.json:
        abort(500)
    MSG_TYPE = request.json.get("message_key", None)  #salary slip,xyz
    print(MSG_TYPE)
    message_detail = mongo.db.notification_msg.find_one({"message_key": MSG_TYPE})
    print(message_detail)
    if message_detail is not None:   
        if message_detail['message_type']:
            message = message_detail['message']
            color = message_detail['color']
            # looping over all the needs check if my message type in that key and if found
            for key in message_needs:
                if message_detail['message_type'] == key:
                    print(message_needs[key])
                    found = True
                    # LOOP OVER THE KEYS inside the need FOR REQUEST
                    for data in message_needs[key]:
                        # print(data)
                        found = False
                        for elem in request.json:
                            print(data, elem)
                            if data == elem:
                                found = True
                        # REQUIREMNT DOES NOT SATISFIED RETURN INVALID REQUEST
                        if found == False:
                            return jsonify(data + " is missing from request"), 400
                    # IF FOUND PROCESS THE REQUEST.JSON DATA
                    if found == True:
                        input = request.json
                        email = input['email']       
                        notifie_user(message=message, email=email,color=color,data=input)
                        return jsonify({"Message": "Sended","Status": True}), 200
        else:
            return jsonify("Invalid Request"), 400
    else:
        return jsonify("No Message Type Available"), 400



@bp.route('/slack', methods=["GET"])
def slack():
    token = tms_load_token()
    print(token)
    sc = SlackClient(token)
    
    data = sc.api_call("conversations.list",
                       types="private_channel",
                       exclude_archived=True)
    data_list = sc.api_call("groups.list", exclude_archived=True)
    channel = []
    print(data)
    detail = data_list['groups']

    for grp in detail:
        if slack in ret['members']:
            channel.append({'value': grp['id'], 'text': grp['name']})
    inner = []
    element = data['channels']
    for chnl in element:
        inner.append({'value': chnl['id'], 'text': chnl['name']})
    total = inner + channel
    result = []
    for elem in total:
        notSame = True
        for chnel in result:
            if ((elem["text"] == chnel["text"])
                    and (elem["value"] == chnel["value"])):
                notSame = False
        if (notSame):
            result.append(elem)
    return jsonify(result)


#Api for schdulers mesg settings
@bp.route('/slack_mesg', methods=["GET", "PUT"])
@jwt_required
@token.admin_required
def slack_schduler():
    if request.method == "GET":
        ret = mongo.db.notification_msg.find({})
        ret = [serialize_doc(doc) for doc in ret]
        return jsonify(ret)
    if request.method == "PUT":
        MSG = request.json.get("message", None)
        MSG_TYPE = request.json.get("message_key", None)
        MSG_ORIGIN = request.json.get("message_origin", None)
        Category = request.json.get("message_type", None)
        MSG_Color = request.json.get("message_color", None)
        Working = request.json.get("working", True)
        slack_channel = request.json.get("slack_channel",[]),
        email_group = request.json.get("email_group",None)

        if not MSG and MSG_TYPE and MSG_ORIGIN:
            return jsonify({"msg": "Invalid Request"}), 400

        ret = mongo.db.notification_msg.update({}, {
           "$set": {
                "message": MSG,
                "message_key": MSG_TYPE,
                "message_origin": MSG_ORIGIN,
                "message_type": Category,
                "message_color": MSG_Color,
                "slack_channel":slack_channel,
                "email_group":email_group
            }
        },upsert=True)
        return jsonify(str(ret))


@bp.route('/tms_settings', methods=["PUT", "GET"])
@jwt_required
@token.admin_required
def tms_setings():
    if request.method == "GET":
        users = mongo.db.tms_settings.find({})
        users = [serialize_doc(doc) for doc in users]
        return jsonify(users)

    if request.method == "PUT":
        webhook_url = request.json.get("webhook_url")
        slack_token = request.json.get("slack_token")
        secret_key = request.json.get("secret_key")
        ret = mongo.db.tms_settings.update({}, {
            "$set": {
                "webhook_url": webhook_url,
                "slack_token": slack_token,
                "secret_key": secret_key
            }
        },upsert=True)
        return jsonify(str(ret))


@bp.route('/mail_settings', methods=["PUT", "GET"])
def mail_setings():
    if request.method == "GET":
       mail = mongo.db.mail_settings.find({},{"mail_password":0})
        mail = [serialize_doc(doc) for doc in mail]
        return jsonify(mail)
    if request.method == "PUT":
        if not request.json:
            abort(500)
        found = True
        for data in Mail_update_needs:
            found = False
            for elem in request.json:
                print(data, elem)
                if data == elem:
                    found = True        
            if found == False:
                return jsonify(data + " is missing from request"),400
        if found == True:
            input = request.json
            MAIL_SERVER = input["mail_server"]
            MAIL_PORT = input["mail_port"]
            MAIL_USE_TLS = input["mail_use_tls"]
            MAIL_USERNAME = input["mail_username"]
            MAIL_PASSWORD = input["mail_password"]
            ret = mongo.db.mail_settings.update({}, {
                "$set": {
                    "mail_server": MAIL_SERVER,
                    "mail_port": MAIL_PORT,
                    "mail_use_tls": MAIL_USE_TLS,
                    "mail_username":MAIL_USERNAME,
                    "mail_password":MAIL_PASSWORD
                }
            },upsert=True)
            return jsonify(str(ret))