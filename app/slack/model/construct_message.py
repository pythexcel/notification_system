from app import mongo
import datetime
import json
import re
import dateutil.parser

from app.slack.model.slack_notification import slack_notification

from app.email.model.email_notification import email_notification
from app.zapier.model.zapier_notification import zapier_notification




def fetch_user_details(req_json=None):
    #status = mongo.db.slack_settings.find_one({},{"_id":0})
    user_slack_details = json.loads(json.dumps(req_json))
    user_email_details = json.loads(json.dumps(req_json))
    user_zapier_details = json.loads(json.dumps(req_json))
    return user_slack_details,user_email_details,user_zapier_details


def construct_message(user_slack_details,user_email_details,user_zapier_details,message,req_json,message_variables,system_require,message_detail):
    system_variable ={"Date":datetime.datetime.utcnow().strftime("%d-%B-%Y")}
    # If for_slack is true in request which coming from tms it will send notification to slack using exist slack apis functionality.
    if message_detail['for_slack'] is True:
        slack_notification(user_slack_details,message,message_detail,message_variables,system_require,system_variable)
    else:
        pass

    # If for_email is true in request which coming from tms it will send notification to email using exist email functionality i didn't make any change in this.
    if message_detail['for_email'] is True:
        email_notification(user_email_details,message,message_detail,message_variables,system_require,system_variable)
    else:
        pass

    # If for_zapier is true in request which coming from tms it will send notification to zapier using webhook.
    if 'for_zapier' in message_detail:
        if message_detail['for_zapier'] is True:
            zapier_notification(user_zapier_details,message,message_detail,message_variables,system_require,system_variable)
        else:
            pass






