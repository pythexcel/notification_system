from app import mongo
from flask import (Blueprint, flash, jsonify, abort, request)
from app.util import serialize_doc
from app import token
from flask_jwt_extended import (JWTManager, jwt_required, create_access_token,
                                get_jwt_identity, get_current_user,
                                jwt_refresh_token_required,
                                verify_jwt_in_request)



bp = Blueprint('slack_settings', __name__, url_prefix='/slack')

@bp.route('/settings', methods=["PUT", "GET"])
# @token.admin_required
def tms_setings():
    if request.method == "GET":
        slack = mongo.db.slack_settings.find_one({},{"_id":0})
        return jsonify(slack)

    if request.method == "PUT":
        slack_token = request.json.get("slack_token")
        if not slack_token:
            return jsonify({"MSG": "Slack Token missing"}), 400
        ret = mongo.db.slack_settings.update({}, {
            "$set": {
                "slack_token": slack_token
            }
        },upsert=True)
        return jsonify({"MSG":"upserted","status":True}), 200
