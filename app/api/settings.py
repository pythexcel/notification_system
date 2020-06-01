import datetime
from app import token
from app import mongo
from flask import (Blueprint, jsonify, request)
from app.services.util import serialize_doc

bp = Blueprint('settings', __name__, url_prefix='/')

@bp.route('/settings', methods=["PUT", "GET"])
#@token.admin_required
def system_settings_setings():
    if request.method == "GET":
        system_settings = mongo.db.system_settings.find_one({},{"_id":0})
        return jsonify(system_settings)

    if request.method == "PUT":
        pdf_allow = request.json.get("pdf",False)
        update_settings = mongo.db.system_settings.update({}, {
            "$set": {
                "pdf": pdf_allow
            }
        },upsert=True)
        return jsonify({"message":"upserted","status":True}), 200
