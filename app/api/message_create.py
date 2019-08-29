from app import mongo
from flask import (Blueprint, flash, jsonify, abort, request)
from app.util import serialize_doc


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
        slack_channel = request.json.get("slack_channel",None),
        email_group = request.json.get("email_group",None)
        channel = request.json.get("channels",None)

        if not MSG and MSG_TYPE and MSG_KEY:
            return jsonify({"msg": "Invalid Request"}), 400

        ret = mongo.db.notification_msg.update({"message_key": MSG_KEY}, {
           "$set": {
                "message": MSG,
                "message_key": MSG_KEY,
                "message_origin": message_origin,
                "message_type": MSG_TYPE,
                "working":Working,
                "message_color": MSG_Color,
                "slack_channel":slack_channel,
                "email_group":email_group,
                "channels":channel
            }
        },upsert=True)
        return jsonify(str(ret))