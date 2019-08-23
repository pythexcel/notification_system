from app import token
from app import mongo
from flask import (Blueprint, flash, jsonify, abort, request)
from app.util import serialize_doc,construct_message,validate_message
from app.config import message_needs
from app.slack_util import slack_message 
from flask_jwt_extended import (JWTManager, jwt_required, create_access_token,
                                get_jwt_identity, get_current_user,
                                jwt_refresh_token_required,
                                verify_jwt_in_request)

bp = Blueprint('notify', __name__, url_prefix='/notify')


@bp.route('/dispatch', methods=["POST"])
def dispatch():
    if not request.json:
        abort(500)
    MSG_KEY = request.json.get("message_key", None)  #salary slip,xyz
    print(MSG_KEY)
    message_detail = mongo.db.notification_msg.find_one({"message_key": MSG_KEY})
    print(message_detail)
    if message_detail and message_detail['message_type'] is not None:   
            message = message_detail['message']
            missing_payload = []
            # looping over all the needs check if my message type in that key and if found
            for key in message_needs:
                if message_detail['message_type'] == key:
                    need_found_in_payload = False
                    # LOOP OVER THE KEYS inside the need FOR REQUEST
                    for data in message_needs[key]:
                        need_found_in_payload = False
                        if data in request.json:
                            need_found_in_payload = True
                        # REQUIREMNT DOES NOT SATISFIED RETURN INVALID REQUEST
                        else:
                            missing_payload.append(data)
                            # return jsonify(data + " is missing from request"), 400
                    # IF FOUND PROCESS THE REQUEST.JSON DATA
                    if not missing_payload:
                        input = request.json
                        user = input['user']
                        try:
                            validate_message(message=message, user=user,req_json=input) 
                            return jsonify({"status":True,"Message":"Sended"}),200 
                        except Exception as error:
                            return(repr(error)),400
                    else:
                        ret = ",".join(missing_payload)
                        return jsonify(ret + " is missing from request"), 400
    else:
        return jsonify("No Message Type Available"), 400

