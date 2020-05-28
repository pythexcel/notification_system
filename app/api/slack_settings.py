from app import mongo
from flask import (Blueprint, flash, jsonify, abort, request,redirect)
from app.util import serialize_doc
from app.config import slack_redirect_url,oauth_url,client_id,client_secret,client_redirect_uri
from app import token
from flask_jwt_extended import (JWTManager, jwt_required, create_access_token,
                                get_jwt_identity, get_current_user,
                                jwt_refresh_token_required,
                                verify_jwt_in_request)

import datetime
import requests as Request

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

@bp.route('/redirect', methods=["GET"])
#@token.admin_required
def slack_redirect():
    code = request.args.get("code")
    state = request.args.get("state")
    state_save = mongo.db.app_state.insert(
        {   
            'state': state,
            'code': code,
            'installed_on': datetime.datetime.now()
        }
    )
    oauth_details = {
        'code': code,
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': client_redirect_uri
    }
    token = Request.post(oauth_url,data=oauth_details)
    token_resp = token.json().get('access_token') 
    save_token = mongo.db.slack_settings.update({}, {
        "$set": {
            "slack_token": token_resp
        }
    },upsert=True)
    return redirect(slack_redirect_url), 302

    