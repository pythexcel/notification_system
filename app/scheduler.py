from app import mongo
from app.util import serialize_doc
import datetime
from bson.objectid import ObjectId
from app.mail_util import send_email


def campaign_mail():
    print("RUNNING...............")
    ret = mongo.db.campaign_users.find_one({"send_status":False})
    if ret is not None:
        mail = ret['email']
        cam = mongo.db.campaigns.find_one({"_id":ObjectId(ret['campaign'])})
        for data in cam['Template']:
            temp = mongo.db.mail_template.find_one({"_id":ObjectId(data)})
            subject = temp['message_subject']
            message_variables = []
            message = temp['message'].split()
            for elem in message:
                if elem[0]=='#':
                    message_variables.append(elem[1:])     
            message_str = temp['message']
            for detail in message_variables:
                if detail in ret:
                    message_str = message_str.replace("#"+detail, ret[detail])
            to = []
            to.append(mail)        
            send_email(message=message_str,recipients=to,subject=subject)

        campaign = mongo.db.campaigns.update({"_id":ObjectId(ret['campaign'])},
            {
                "$set": {
                        "cron_status": True
                    }
                    })

        user_status = mongo.db.campaign_users.update({"_id":ObjectId(ret['_id'])},
            {
                "$set": {
                        "send_status": True
                    }
                    })
        print("EMAIL_SENDED...............")
    
    else:
        pass    

