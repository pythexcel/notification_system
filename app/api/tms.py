from app import token
from app import mongo
from flask import (Blueprint, flash, jsonify, abort, request)
import dateutil.parser
from bson.objectid import ObjectId
from slackclient import SlackClient
import requests
import datetime
from app.util import slack_msg, slack_message
from flask_jwt_extended import (JWTManager, jwt_required, create_access_token,
                                get_jwt_identity, get_current_user,
                                jwt_refresh_token_required,
                                verify_jwt_in_request)

bp = Blueprint('tms', __name__, url_prefix='/tms')

@bp.route('/checkin_send_message', methods=["POST"])
def post_report():
    if not request.json:
        abort(500)
    msg_type = request.json.get("type",None)
    print(msg_type)
    if msg_type == "Check-in":
        print("hello")
        slackReport = request.json.get("slackReport", None)
        highlight = request.json.get("highlight", "")
        slackChannels = request.json.get("slackChannels", [])
        slack = request.json.get("slack", None)
        date_time = datetime.datetime.utcnow()
        formatted_date = date_time.strftime("%d-%B-%Y")
        slack_message(msg="<@" + slack + ">!" + ' '
                    'have created daily chechk-in at' + ' ' +
                    str(formatted_date))
        if len(highlight) > 0:
            slack_msg(channel=slackChannels,
                    msg="<@" + slack + ">!" + "\n" + "Report: " + "\n" +
                    slackReport + "" + "\n" + "Highlight: " + highlight)
        else:
            slack_msg(channel=slackChannels,
                    msg="<@" + slack + ">!" + "\n" + "Report: " + "\n" +
                    slackReport + "")
    elif msg_type == "Weekly":
        print("Nope")
        slack = request.json.get("slack", None)
        date_time = datetime.datetime.utcnow()
        formatted_date = date_time.strftime("%d-%B-%Y")
        slack_message(msg="<@" + slack + ">!" + ' '
                    'have created weekly report at' + ' ' +
                    str(formatted_date))

    return jsonify({"msg":"Done"}),200     
