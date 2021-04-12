#from app import mongo
from flask import current_app as app



#function for get notification message by message key
def get_notification_function_by_key(mongo,MSG_KEY = None):
    if MSG_KEY is not None: 
        message_detail = mongo.notification_msg.find_one({"message_key": MSG_KEY})
        if message_detail is not None:
            working_check = mongo.notification_msg.find_one({"message_key": MSG_KEY,"working":True})
            if working_check is not None:
                return message_detail
            else:
                return False
        else:
            raise Exception("No message available for this key")
    else:
        raise Exception("Message key is none")





