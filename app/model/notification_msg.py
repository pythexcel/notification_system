from app import mongo



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