from app.slack.util.make_message import MakeMessage
from app.slack.util.fetch_channels import FetchRecipient,FetchChannels
from app.slack.model.slack_util import slack_message,slack_id
import json
from app import mongo



def zapier_notification(user_detail,message,message_detail,message_variables,system_require,system_variable):
        email = ""
        #Fetching username from tms request data.
        if "user" in user_detail:
            username = user_detail['user']['name']
        else:
            username = ""
        #Fetching email id for send email to notification related user
        if "work_email" in user_detail['user']:
            email = user_detail['user']['work_email']
        else:
            if "email" in user_detail['user']:
                email = user_detail['user']['email']
            else:
                pass
        #If email data is available in message request like notification subject etc defined already and its available in db in message it will take subject from there 
        #Else message key will be email subject.
        if 'emailData' in user_detail:
            if 'subject' in user_detail['emailData']:
                subject = user_detail['emailData']['subject']
            else:
                subject = message_detail['message_key']             
        else:
            subject = message_detail['message_key']             
        #For phone data if phone details availabl in request it will take phone number from there.
        if 'PhoneData' in user_detail:
            phone = user_detail['PhoneData']
        else:
            phone = ""

        #Here we are making two messages one for send to slack and on for default can send any other platform.
        #Difference between both just in slack message have slack if and in default message have username.
        if 'user' in user_detail and user_detail['user'] is not None:
            slack_details = True
            try:
                slack = slack_id(user_detail['user']['email'])# Fetching user slack id by email using slack api
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
        #This function will return us proper message with user slackid which need to send to user.
        slackmessage = MakeMessage(message_str=message,message_variables=message_variables,user_detail=user_detail,system_require=system_require,system_variable=system_variable)
        #I make a common function for fetch channels from tms requests.like on which slack or personal we want to send message.
        channels = FetchChannels(user_detail=user_detail,message_detail=message_detail)

        if slack_details is not False:
                user_detail['user'] = username
        else:
            pass
        #calling same function for make default message with username instead of slack id 
        defaultmessage = MakeMessage(message_str=message,message_variables=message_variables,user_detail=user_detail,system_require=system_require,system_variable=system_variable)
        #I make a common function for fetch recipients from tms requests.like on which email we want to send message.
        recipient = FetchRecipient(user_detail=user_detail,message_detail=message_detail)
        #if no default recipients available then it will take user email.
        if not recipient:
            recipient = [email]
        #Will inser mesaage payload in collection from there zapier cron will take it and hit webhook
        if channels or recipient is not None:
            mongo.db.messages_cron.insert_one({
                "cron_status":False,
                "type": "zapier",
                "slackmessage":slackmessage,
                "defaultmessage":defaultmessage,
                "recipients":recipient,
                "channel":channels,
                "phone":phone,
                "subject": subject,
                "req_json": user_detail,
                "message_detail":message_detail
            }).inserted_id
        else:
            pass