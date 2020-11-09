import datetime
#from app import mongo




#function for update messages into collection
def update_recruit_mail_msg(mongo,phone=None,phone_message=None,phone_issue=None,message=None,subject=None,to=None,is_reminder=None):
    if message and subject and to is not None:
        id = mongo.recruit_mail.update({"message":message,"subject":subject,"to":to},{
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
