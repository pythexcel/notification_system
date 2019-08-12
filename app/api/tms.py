from app import token
from app import mongo
from flask import (Blueprint, flash, jsonify, abort, request)
import dateutil.parser
from bson.objectid import ObjectId
from slackclient import SlackClient
import requests
import datetime
from app.config import default
from app.util import slack_msg, slack_message,serialize_doc
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
        return jsonify({"msg":"Done"}),200                
    elif msg_type == "Weekly":
        print("Nope")
        slack = request.json.get("slack", None)
        date_time = datetime.datetime.utcnow()
        formatted_date = date_time.strftime("%d-%B-%Y")
        slack_message(msg="<@" + slack + ">!" + ' '
                    'have created weekly report at' + ' ' +
                    str(formatted_date))
        return jsonify({"msg":"Done"}),200            
    elif msg_type == "Monthly":
        print("Hope")
        slack = request.json.get("slack",None)
        slack_message(msg="<@" + slack + ">!" + ' '
                                'have created monthly report')
        return jsonify({"msg":"Done"}),200                        

        
@bp.route('/schdulers_settings', methods=["GET","PUT"])
@jwt_required
@token.admin_required
def schdulers_setings():
    if request.method == "GET":
        ret = mongo.db.schdulers_setting.find({
        })
        ret = [serialize_doc(doc) for doc in ret]
        return jsonify(ret)

    if request.method == "PUT":
        monthly_remainder = request.json.get("monthly_remainder")
        weekly_remainder = request.json.get("weekly_remainder")
        recent_activity = request.json.get("recent_activity")
        review_activity = request.json.get("review_activity")
        monthly_manager_reminder = request.json.get("monthly_manager_reminder")
        revew_360_setting=request.json.get("revew_360_setting",True)
        missed_reviewed=request.json.get("missed_reviewed",True)
        skip_review_setting=request.json.get("managerSkip",True)
        weekly_automated=request.json.get("weekly_automated",True)
        ret = mongo.db.schdulers_setting.update({
            },{
                "$set":{
                "monthly_remainder": monthly_remainder,
                "weekly_remainder": weekly_remainder,
                "recent_activity": recent_activity,
                "review_activity": review_activity,
                "monthly_manager_reminder": monthly_manager_reminder,
                "revew_360_setting":revew_360_setting,
                "missed_reviewed":missed_reviewed,
                "skip_review":skip_review_setting,
                "weekly_automated":weekly_automated
            }}, upsert=True)
        return jsonify(str(ret))

        
        #Api for schdulers mesg settings
@bp.route('/schduler_mesg', methods=["GET","PUT"])
@jwt_required
@token.admin_required
def slack_schduler():
    if request.method == "GET":
        ret = mongo.db.schdulers_msg.find({
        })
        ret = [serialize_doc(doc) for doc in ret]
        return jsonify([default] if not ret else ret)
    if request.method == "PUT":
        monthly_remainder = request.json.get("monthly_remainder")
        weekly_remainder1 = request.json.get("weekly_remainder1")
        weekly_remainder2 = request.json.get("weekly_remainder2")
        review_activity = request.json.get("review_activity")
        monthly_manager_reminder = request.json.get("monthly_manager_reminder")
        missed_checkin = request.json.get("missed_checkin")
        weekly_report_mesg=request.json.get("weekly_report_mesg")
        monthly_report_mesg=request.json.get("monthly_report_mesg")
        missed_review_msg = request.json.get("missed_reviewed_mesg")
        ret = mongo.db.schdulers_msg.update({
        }, {
            "$set": {
                "monthly_remainder": monthly_remainder,
                "weekly_remainder1": weekly_remainder1,
                "weekly_remainder2":weekly_remainder2,
                "review_activity":review_activity,
                "monthly_manager_reminder":monthly_manager_reminder,
                "missed_checkin":missed_checkin,
                "weekly_report_mesg":weekly_report_mesg,
                "monthly_report_mesg":monthly_report_mesg,
                "missed_reviewed_mesg":missed_review_msg
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
    