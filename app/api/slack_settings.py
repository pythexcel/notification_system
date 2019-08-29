from app import mongo
from flask import (Blueprint, flash, jsonify, abort, request)
from app.util import serialize_doc



bp = Blueprint('slack_settings', __name__, url_prefix='/slack')

@bp.route('/settings', methods=["PUT", "GET"])
def tms_setings():
    if request.method == "GET":
        slack = mongo.db.slack_settings.find_one({},{"_id":0})
        return jsonify(slack)

    if request.method == "PUT":
        slack_token = request.json.get("slack_token")
        slack_notifcation = request.json.get("slack_notification")
        send_email = request.json.get("send_email")
        mobile_message = request.json.get("mobile_message")
        ret = mongo.db.slack_settings.update({}, {
            "$set": {
                "slack_token": slack_token,
                "slack_notfication":slack_notifcation,
                "send_email":send_email,
                "mobile_message":mobile_message
            }
        },upsert=True)
        return jsonify(str(ret))
