import datetime
import smtplib,ssl    
from app import mongo
from app.config import smtp_counts
from bson import ObjecstId

def serialize_doc(doc):
    doc["_id"] = str(doc["_id"])
    return doc

def validate_smtp( username, password, port, smtp):
    if port == 587:   
        context = ssl.create_default_context()     
        mail = smtplib.SMTP(str(smtp), port)
        mail.ehlo() 
        mail.starttls(context=context) 
        mail.ehlo() 
        mail.login(username,password)
    else:
        mail = smtplib.SMTP_SSL(str(smtp), port)
        mail.login(username,password)
    mail.quit()

    
def validate_smtp_counts(smtp_ids):
    final_ids = []
    for id in smtp_ids:
        final_ids.append(ObjectId(id))
    smtp_mail = mongo.db.mail_settings.find({"origin": "CAMPAIGN","_id": {"$in":final_ids}})
    smtp_mail = [serialize_doc(doc) for doc in smtp_mail]
    valid_smtp = dict()
    if smtp_mail:
        for index, mail in enumerate(smtp_mail):
            if mail['mail_server'] in smtp_counts:
                # here below is the condtions we will check for smtp counts and values 
                today = datetime.datetime.today()
                next_day = datetime.datetime.today() + datetime.timedelta(days=1)
                smtp_validate = mongo.db.smtp_count_validate.find_one({"smtp":mail['mail_server'],"email":mail['mail_username'],
                "created_at":{
                "$gte": datetime.datetime(today.year, today.month, today.day),
                "$lte": datetime.datetime(next_day.year, next_day.month, next_day.day)}})
                if smtp_validate is not None:
                    if smtp_validate['count'] < smtp_counts[mail['mail_server']]:
                        valid_smtp.update({
                            "mail_username":mail['mail_username'],
                            "mail_password":mail['mail_password'],
                            "mail_server":mail['mail_server'],
                            "mail_port":mail['mail_port'],
                            "count_details":str(smtp_validate['_id'])})
                        return valid_smtp
                    elif len(smtp_mail) == index + 1:
                        raise Exception("SMTP OVER") 
                else:
                    smtp_validate_insert = mongo.db.smtp_count_validate.insert_one({
                        "smtp":mail['mail_server'],
                        "email":mail['mail_username'],
                        "created_at": today,
                        "count": 0
                    }).inserted_id
                    valid_smtp.update({
                        "mail_username":mail['mail_username'],
                        "mail_password":mail['mail_password'],
                        "mail_server":mail['mail_server'],
                        "mail_port":mail['mail_port'],
                        "count_details":str(smtp_validate_insert)})      
                    return valid_smtp
    else:
        raise Exception("Smtp is not available")
