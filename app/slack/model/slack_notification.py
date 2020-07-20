from app.slack.model.slack_util import slack_id
from app.slack.util.make_message import MakeMessage
from app.slack.util.fetch_channels import FetchChannels
from app import mongo




def slack_notification(user_detail,message,message_detail,message_variables,system_require,system_variable):
    if 'user' in user_detail and user_detail['user'] is not None:
        slack_details = True
        try:
            slack = slack_id(user_detail['user']['email']) # Fetching user slack id by email using slack api
        except Exception:
            slack_details = False   
        #If there is slack id available then it will put slack it in message else will put username
        if slack_details is False:    
            user_detail['user'] = user_detail['user']['name']
        else:    
            user_detail['user'] = "<@" + slack + ">"
    else:
        pass            
    # I make common function for message create and replace all data @data: variables according to requested notification from tms
    #This function will return us proper message with slack id which need to send to user.
    message_str = MakeMessage(message_str=message,message_variables=message_variables,user_detail=user_detail,system_require=system_require,system_variable=system_variable)
    #I make a common function for fetch channels from tms requests.like on which slack or personal we want to send message.
    channels = FetchChannels(user_detail=user_detail,message_detail=message_detail)
    #If channels available for send notification it will insert notification info in collection.
    if channels:                                                   
        mongo.db.messages_cron.insert_one({
            "cron_status":False,
            "type": "slack",
            "message":message_str,
            "channel":channels,
            "req_json": user_detail,
            "message_detail":message_detail
        }).inserted_id
    else:
        pass
    