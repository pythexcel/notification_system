import datetime
from app import token
from app import mongo
from flask import (Blueprint, jsonify, request)
from app.services.util import serialize_doc


bp = Blueprint('slack_settings', __name__, url_prefix='/slack')

@bp.route('/settings', methods=["PUT", "GET"])
#@token.admin_required
def slack_seting():
    if request.method == "GET":
        slack = mongo.db.slack_settings.find_one({},{"_id":0})
        return jsonify(slack)

    if request.method == "PUT":
        slack_token = request.json.get("slack_token")
        if not slack_token:
            return jsonify({"message": "Slack Token missing"}), 400
        ret = mongo.db.slack_settings.update({}, {
            "$set": {
                "slack_token": slack_token
            }
        },upsert=True)
        return jsonify({"message":"upserted","status":True}), 200
