from app.auth import token
from app import mongo
from flask import (Blueprint, flash, jsonify, abort, request,url_for,send_from_directory)
from app.util.serializer import serialize_doc
from app.slack.util.slack_util import slack_message,slack_id
from flask_jwt_extended import (JWTManager, jwt_required, create_access_token,
                                get_jwt_identity, get_current_user,
                                jwt_refresh_token_required,
                                verify_jwt_in_request)
import json
from flask import current_app as app
from app.slack.model.construct_payload import contruct_payload_from_request
from app.slack.model.notification_msg import get_notification_function_by_key

bp = Blueprint('dispatch', __name__, url_prefix='/notify')


#dispatch was made to send particular message on slack but those message can be sended on email too
@bp.route('/dispatch', methods=["POST"])
#@token.authentication
def construct_dispatch_message_to_slack():
    if not request.json:
        abort(500)
    MSG_KEY = request.json.get("message_key", None)
    try:
        message_detail = get_notification_function_by_key(MSG_KEY=MSG_KEY)
        contruct_payload_from_request(message_detail=message_detail,input=request.json)
        return jsonify({"status":True,"Message":"Sended"}),200 
    except Exception as error:
        return(str(error)),400


#Api for test slack token and notifications is working or by email address
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



