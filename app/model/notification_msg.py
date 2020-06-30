import re
import datetime
from app import mongo
from app.config import dates_converter
from app.util import serialize_doc
from bson.objectid import ObjectId
from flask import current_app as app

#function for get notification message by message key
def get_notification_function_by_key(MSG_KEY = None):
    if MSG_KEY is not None: 
        message_detail = mongo.db.notification_msg.find_one({"message_key": MSG_KEY})
        if message_detail is not None:
            return message_detail
        else:
            raise Exception("No message available for this key")
    else:
        raise Exception("Message key is none")



#function for fetch details from db by date about interview reminders
def fetch_interview_reminders(date=None):
    if date is not None:
        details = mongo.db.reminder_details.aggregate([
            { '$match' : {
                'date': { '$gte' : date }
            }},
        {
            '$group' : {
                '_id' : {
                    '$dateToString': { 'format': "%Y-%m-%d", 'date': "$date" }} , 'total' : { '$sum' : 1}
            }},
            { '$sort': { '_id': 1 } }
            ])
        details =[serialize_doc(doc) for doc in details]
        return details
    else:
        raise Exception("Date not should be None")


#function for update messages into collection
def update_recruit_mail_msg(phone=None,phone_message=None,phone_issue=None,message=None,subject=None,to=None,is_reminder=None):
    if message and subject and to is not None:
        id = mongo.db.recruit_mail.update({"message":message,"subject":subject,"to":to},{
        "$set":{
            "phone":phone,
            "phone_message": phone_message,
            "phone_issue": phone_issue,
            "message": message,
            "subject": subject,
            "to":to,
            "is_reminder":is_reminder,
            "date": datetime.datetime.now()
        }},upsert=True)
    else:
        raise Exception("Message subject and recipents not should be none")
