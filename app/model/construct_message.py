from app import mongo
import datetime
from app.util.slack_util import slack_message,slack_id
from app.model.sendmail import send_email
import json
from bson.objectid import ObjectId
import re
import dateutil.parser
from app.util.make_message import MakeMessage
from app.util.fetch_channels import FetchChannels,FetchRecipient
from app.model.slack_notification import slack_notification
from app.model.email_notification import email_notification
from app.model.zapier_notification import zapier_notification




def construct_message(message=None,req_json=None,message_variables=None,system_require=None,message_detail=None):
    system_variable ={"Date":datetime.datetime.utcnow().strftime("%d-%B-%Y")}
    status = mongo.db.slack_settings.find_one({},{"_id":0})
    req_json = json.loads(json.dumps(req_json))
    user_detail = req_json
    # If for_slack is true in request which coming from tms it will send notification to slack using exist slack apis functionality.
    if message_detail['for_slack'] is True:
        slack_notification(user_detail,message,message_detail,message_variables,system_require,system_variable)
    else:
        pass

    # If for_email is true in request which coming from tms it will send notification to email using exist email functionality i didn't make any change in this.
    if message_detail['for_email'] is True:
        email_notification(user_detail,message,message_detail,message_variables,system_require,system_variable)
    else:
        pass
    # If for_zapier is true in request which coming from tms it will send notification to zapier using webhook.
    if message_detail['for_zapier'] is True:
        zapier_notification(user_detail,message,message_detail,message_variables,system_require,system_variable)
    else:
        pass








