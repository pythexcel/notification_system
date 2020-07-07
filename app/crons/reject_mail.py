import re
from app import mongo
from app.util.serializer import serialize_doc
import datetime
import dateutil.parser
from bson.objectid import ObjectId
from app.model.sendmail import send_email
from flask import current_app as app
import time
import email


def reject_mail():
    ret = mongo.db.rejection_handling.find_one({"send_status":False})
    if ret is not None:
        if ret['smtp_email'] is not None:
            message = ret['message']
            time = ret['rejection_time']  
            time_update = dateutil.parser.parse(time).strftime("%Y-%m-%dT%H:%M:%SZ")
            rejected_time = datetime.datetime.strptime(time_update,'%Y-%m-%dT%H:%M:%SZ')
            diffrence = datetime.datetime.utcnow() - rejected_time
            if diffrence.days >= 1:
                to = []
                mail = ret['email']  
                to.append(mail)
                mail_details = mongo.db.mail_settings.find_one({"mail_username":str(ret['smtp_email']),"origin": "RECRUIT"})
                if mail_details is not None:
                    send_email(message=message,recipients=to,subject='REJECTED',sending_mail=mail_details['mail_username'],sending_password=mail_details['mail_password'],sending_port=mail_details['mail_port'],sending_server=mail_details['mail_server'])
                    user_status = mongo.db.rejection_handling.remove({"_id":ObjectId(ret['_id'])})
                else:
                    pass
            else:
                pass
        else:
            pass
    else:
        pass
