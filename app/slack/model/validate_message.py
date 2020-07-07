import datetime
import re

from app.slack.model.construct_message import construct_message



def validate_message(user=None,message=None,req_json=None,message_detail=None):
    system_variable ={"Date":datetime.datetime.utcnow().strftime("%d-%B-%Y")}
    message_special = message.split()
    message_variables = []
    system_require = []
    missing_payload = []
    rex = re.compile('\@[a-zA-Z0-9/_]+\:')
    for data in message_special:
        reg = rex.match(data)
        if reg is not None:
            vl = data.find(":") - len(data)
            message_variables.append(data[1:vl])                              
    for data in system_variable:
        if data in message_variables:
            system_require.append(data)
            message_variables.remove(data)
        else:
            pass           
    need_found_in_payload = True
    for data in message_variables:
        need_found_in_payload = False
        if data in req_json:
            need_found_in_payload = True
        else:
            # HERE the logic behind this is if someone wants to send multiple things in req then variable data will be a dictionary
            if data in req_json['data']:
                need_found_in_payload = True
            else:
                missing_payload.append(data)
    if not missing_payload:
        construct_message(message=message,message_variables=message_variables,
                        req_json=req_json,system_require=system_require,message_detail=message_detail)             
    else:
        ret = ",".join(missing_payload)
        raise Exception("These data are missing from payload: " + ret)      
