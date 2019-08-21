from app import mongo
from flask import (Blueprint, flash, jsonify, abort, request)
from app.util import serialize_doc



bp = Blueprint('slack_settings', __name__, url_prefix='/slack')

@bp.route('/settings', methods=["PUT", "GET"])
def tms_setings():
    if request.method == "GET":
        slack = mongo.db.slack_settings.find({})
        slack = [serialize_doc(doc) for doc in users]
        return jsonify(slack)

    if request.method == "PUT":
        slack_token = request.json.get("slack_token")
        ret = mongo.db.slack_settings.update({}, {
            "$set": {
                "slack_token": slack_token
            }
        },upsert=True)
        return jsonify(str(ret))
