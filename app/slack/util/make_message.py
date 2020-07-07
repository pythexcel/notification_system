#function for make message from message request.
#This function will replace all @data: valiables with requested data and will make a proper message with username or slackid as same as before nothing change in this
def MakeMessage(message_str=None,message_variables=None,user_detail=None,system_require=None,system_variable=None):
    for data in message_variables:
        if data in user_detail:
            if user_detail[data] is None:
                user_detail[data] = "N/A"
            message_str = message_str.replace("@"+data+":", user_detail[data])
        else:
            if 'data' in user_detail:
                if data in user_detail['data']:
                    if user_detail['data'][data] is None:
                        user_detail['data'][data] = "N/A"
                    message_str = message_str.replace("@"+data+":", user_detail['data'][data])    
    for elem in system_require:
        if elem in system_variable:  
            message_str = message_str.replace("@"+elem+":", system_variable[elem])
    return message_str
