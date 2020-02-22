from app import mongo
from flask import (Blueprint, flash, jsonify, abort, request)
from app.util import serialize_doc
from app import token
from flask_jwt_extended import (JWTManager, jwt_required, create_access_token,
                                get_jwt_identity, get_current_user,
                                jwt_refresh_token_required,
                                verify_jwt_in_request)

import datetime

bp = Blueprint('settings', __name__, url_prefix='/')

@bp.route('/settings', methods=["PUT", "GET"])
@token.admin_required
def system_settings_setings():
    if request.method == "GET":
        system_settings = mongo.db.system_settings.find_one({},{"_id":0})
        return jsonify(system_settings)

    if request.method == "PUT":
        pdf_allow = request.json.get("pdf",False)
        ret = mongo.db.system_settings.update({}, {
            "$set": {
                "pdf": pdf_allow
            }
        },upsert=True)
        return jsonify({"message":"upserted","status":True}), 200
