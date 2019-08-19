from app import token
from app import mongo
from flask import (Blueprint, flash, jsonify, abort, request)
import dateutil.parser
from bson.objectid import ObjectId
from slackclient import SlackClient
import requests
import datetime
from app.config import default, simple_message_needs, Notification_message_needs
from app.util import slack_msg, slack_message, serialize_doc, slack_attach,notifie_user
from flask_jwt_extended import (JWTManager, jwt_required, create_access_token,
                                get_jwt_identity, get_current_user,
                                jwt_refresh_token_required,
                                verify_jwt_in_request)

bp = Blueprint('tms', __name__, url_prefix='/tms')


@bp.route('/send_message', methods=["POST"])
def post_report():
    if not request.json:
        abort(500)
    found = True
    # LOOP OVER THE NEEDS FOR REQUEST
    for data in simple_message_needs:
        # print(data)
        found = False
        for elem in request.json:
            print(data, elem)
            if data == elem:
                found = True
        # REQUIREMNT DOES NOT SATISFIED RETURN INVALID REQUEST        
        if found == False:
            return jsonify(data + " is missing from request"),400
    # IF FOUND PROCESS THE REQUEST.JSON DATA
    if found == True:
        input = request.json
        msg_type = input['message_category']
        slack = input['slack']
        slackReport = input['slackReport']
        slackChannels = input['slackChannels']
        email = input['email']
        highlight = input['highlight']
        date_time = datetime.datetime.utcnow()
        formatted_date = date_time.strftime("%d-%B-%Y")
        ret = mongo.db.notification_msg.find_one({"message_type": msg_type})
        if ret is not None:
            if 'message' in ret:
                mesg = ret['message']
                 # here replacing slack_id in message with current date and time same pattern is followed in TMS  
                message = mesg.replace("@Date",formatted_date)
                # Here replacing slack id in the message with slack id came from request same pattern is followed in TMS
                sl_mesg = message.replace("@Slack_id:", "<@" + slack + ">!")
                # field "color" here cannot be put in message string 
                attachments=[{
                            "text": sl_mesg,
                            "color": ret['message_color']
                        }]
                notifie_user(attachments=attachments,message=message,email=email) 
                if len(highlight) > 0:
                    slack_msg(channel=slackChannels,
                                msg="<@" + slack + ">!",
                                attachments=[{
                                    "text":
                                    "Report: " + "\n" + slackReport + "" +
                                    "\n" + "Highlight: " + highlight
                                }])
                else:
                    slack_msg(channel=slackChannels,
                                msg="<@" + slack + ">!",
                                attachments=[{
                                    "text": "Report: " + "\n" + slackReport,
                                    "color": ret['message_color']
                                }])
                return jsonify({"Message": "Sended", "Status": True}), 200
            else:
                return jsonify("Invalid Request"), 400
        else:
            return jsonify("No Message Type Available"), 400

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
        MSG = request.json.get("Message", None)
        MSG_TYPE = request.json.get("Message_Type", None)
        MSG_ORIGIN = request.json.get("Message_Origin", None)
        Category = request.json.get("Message_Category", None)
        MSG_Color = request.json.get("Message_Color", None)
        Working = request.json.get("Working", True)
        unique_key = request.json.get("Unique_key")

        if not MSG and MSG_TYPE and MSG_ORIGIN:
            return jsonify({"msg": "Invalid Request"}), 400

        ret = mongo.db.notification_msg.update({}, {
            "$set": {
                "Message": MSG,
                "Message_Type": MSG_TYPE,
                "Message_Origin": MSG_ORIGIN,
                "Message_Category": Category,
                "Unique_key": unique_key,
                "Message_Color": MSG_Color
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
