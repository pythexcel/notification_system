from app.config import message_needs

from app.slack.model.validate_message import validate_message



def contruct_payload_from_request(mongo,message_detail=None,input=None):
    if message_detail and input is not None:
        if 'message' in message_detail:
            message = message_detail['message']
            missing_payload = []
            # looping over all the needs check if my message type in that key and if found
            for key in message_needs:
                if message_detail['message_type'] == key:
                    need_found_in_payload = False
                    # LOOP OVER THE KEYS inside the need FOR REQUEST
                    for data in message_needs[key]:
                        need_found_in_payload = False
                        if data in input:
                            need_found_in_payload = True
                        # REQUIREMNT DOES NOT SATISFIED RETURN INVALID REQUEST
                        else:
                            missing_payload.append(data)
                            # return jsonify(data + " is missing from request"), 400
                    # IF FOUND PROCESS THE REQUEST.JSON DATA
                    if not missing_payload:
                        try:
                            return message,message_detail,input
                            #validate_message(message=message,message_detail=message_detail,req_json=input) 
                        except Exception as error:
                            return(repr(error)),400
                    else:
                        ret = ",".join(missing_payload)
                        raise Exception(ret + " is missing from request")
        else:
            raise Exception("Message not available in message details")
    else:
        raise Exception("MessageDetails and input not should be None")
