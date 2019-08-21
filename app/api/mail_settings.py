from app import mongo
from flask import (Blueprint, flash, jsonify, abort, request)
from app.util import serialize_doc
from app.config import Mail_update_needs


bp = Blueprint('mail_settings', __name__, url_prefix='/mail_settings')

@bp.route('/mail_settings', methods=["PUT", "GET"])
def mail_setings():
    if request.method == "GET":
       mail = mongo.db.mail_settings.find({},{"mail_password":0})
       mail = [serialize_doc(doc) for doc in mail]
       return jsonify(mail)
    if request.method == "PUT":
        if not request.json:
            abort(500)
        found = True
        for data in Mail_update_needs:
            found = False
            for elem in request.json:
                print(data, elem)
                if data == elem:
                    found = True        
            if found == False:
                return jsonify(data + " is missing from request"),400
        if found == True:
            input = request.json
            MAIL_SERVER = input["mail_server"]
            MAIL_PORT = input["mail_port"]
            MAIL_USE_TLS = input["mail_use_tls"]
            MAIL_USERNAME = input["mail_username"]
            MAIL_PASSWORD = input["mail_password"]
            ret = mongo.db.mail_settings.update({}, {
                "$set": {
                    "mail_server": MAIL_SERVER,
                    "mail_port": MAIL_PORT,
                    "mail_use_tls": MAIL_USE_TLS,
                    "mail_username":MAIL_USERNAME,
                    "mail_password":MAIL_PASSWORD
                }
            },upsert=True)
            return jsonify(str(ret))