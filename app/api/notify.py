from app import token
from app import mongo
from flask import (Blueprint, flash, jsonify, abort, request)
from app.util import serialize_doc,construct_message,validate_message
from app.config import message_needs,messages
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
    missed_req = {}
    message_detail = mongo.db.notification_msg.find_one({"message_key": MSG_KEY})
    # finding data of payload from request key via json
    for data in messages:
        if data['message_key'] == MSG_KEY:
            missed_req = data
    print(missed_req.items())
    print(message_detail)      
    # below will checki if message detail is completely empty return data from json or else if its any value is none replace it from json data
    if message_detail is not None:
        update = message_detail.update((k,v) for k,v in missed_req.items() if v is not None)
    else:
        message_detail = missed_req
    if message_detail and message_detail['message_type'] is not None:   
            message = message_detail['message']
            slack_channels = message_detail['slack_channel']
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
                        try:
                            validate_message(message=message,slack_channel=slack_channels,req_json=input) 
                            return jsonify({"status":True,"Message":"Sended"}),200 
                        except Exception as error:
                            return(repr(error)),400
                    else:
                        ret = ",".join(missing_payload)
                        return jsonify(ret + " is missing from request"), 400
    else:
        return jsonify("No Message Type Available"), 400

