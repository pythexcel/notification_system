from app.slack.util.make_message import MakeMessage
from app.slack.util.fetch_channels import FetchRecipient
import json
from app import mongo
from app.email.model.template_making import fetch_recipients_by_mode,slack_fetch_recipients_by_mode
from app.push_notification.util.push_notification import Push_notification

def email_notification(user_detail,message,message_detail,message_variables,system_require,system_variable):
    if 'user' in user_detail and user_detail['user'] is not None:
        username = json.loads(json.dumps(user_detail['user']['email']))
        name = username.split('@')[0]
        user_detail['user'] = name
    else:
        pass    
    # I make common function for message create and replace all data @data: variables according to requested notification from tms
    #This function will return us proper message with username which need to send to user.
    message_str = MakeMessage(message_str=message,message_variables=message_variables,user_detail=user_detail,system_require=system_require,system_variable=system_variable)

    if 'emailData' in user_detail:
        if 'subject' in user_detail['emailData']:
            subject = user_detail['emailData']['subject']
        else:
            subject = message_detail['message_key']             
    else:
        subject = message_detail['message_key']             
    sender_name = None
    if "to" in user_detail:
        if "sender_name" in user_detail:
            sender_name = user_detail['sender_name']
        else:
            sender_name = None
        if "SlackEmail" in user_detail:
            if 'fcm_registration_id' in user_detail:
                pushmsg =message_str
                pushmsg = pushmsg.replace("\n","")
                Push_notification(message=pushmsg,subject=subject,fcm_registration_id=user_detail['fcm_registration_id'])
            recipient = slack_fetch_recipients_by_mode(user_detail)
            message_str = message_str.replace("\n","<br>")
    else:
        #I make a common function for fetch recipients from tms requests.like on which email we want to send message.
        recipient = FetchRecipient(user_detail=user_detail,message_detail=message_detail)
        #if no default recipients available then it will take user email.
        if not recipient:
            recipient = [username]
        #If channels available for send notification it will insert notification info in collection.
    mongo.db.messages_cron.insert_one({
        "cron_status":False,
        "type": "email",
        "message":message_str,
        "recipients":recipient,
        "subject": subject,
        "req_json": user_detail,
        "sender_name":sender_name,
        "message_detail":message_detail
    }).inserted_id
