import re
from app import mongo
from app.util.serializer import serialize_doc
import datetime
import dateutil.parser
from bson.objectid import ObjectId
from app.model.validate_smtp import validate_smtp_counts
from app.util.validate_smtp import validate_smtp
from app.email.model.sendmail import send_email
from flask import current_app as app
import time



def update_completion_time():
    campaigns = mongo.db.campaigns.find({"$or": [{"status": "Running"}, {"status": "Completed"}]})
    campaigns = [serialize_doc(doc) for doc in campaigns]
    for campaign in campaigns:
        delay= campaign['delay']
        smtp = campaign['smtps']
        campaign_users = mongo.db.campaign_users.find({"campaign":campaign['_id'],"send_status": False})
        campaign_users = [serialize_doc(doc) for doc in campaign_users]
        ids = len(campaign_users)
        total_time = (float(ids)* delay / float(len(smtp)))
        if total_time <= 60:
            total_time = round(total_time,2)
            total_expected_time = "{} second".format(total_time)
        elif total_time>60 and total_time<=3600:
            total_time = total_time/60
            total_time = round(total_time,1)
            total_expected_time = "{} minutes".format(total_time)
        elif total_time>3600 and total_time<=86400:
            total_time = total_time/3600
            total_time = round(total_time,1)
            total_expected_time = "{} hours".format(total_time)
        else:
            total_time = total_time/86400
            total_time = round(total_time,1)
            total_expected_time = "{} days".format(total_time)
        campaign = mongo.db.campaigns.update({"_id": ObjectId(campaign['_id'])},{
            "$set": {
                "total_expected_time_of_completion": total_expected_time
            }
        })


def campaign_details():
    campaigns = mongo.db.campaigns.find({})
    campaigns = [serialize_doc(doc) for doc in campaigns]
    for campaign in campaigns:
        if campaign is not None:
            campaign_users = mongo.db.campaign_users.find({"campaign":campaign['_id'],"already_unsub" : False})
            campaign_users = [serialize_doc(doc) for doc in campaign_users]
            if campaign_users:
                seen_users = mongo.db.mail_status.find({"campaign":campaign['_id'],"seen": True})
                seen_users = [serialize_doc(doc) for doc in seen_users]
                seen_rate = 0
                if seen_users:
                    seen_rate = len(seen_users) * 100 / len(campaign_users)
                clicked_user = mongo.db.mail_status.find({"campaign":campaign['_id'],"clicked": True})
                clicked_user = [serialize_doc(doc) for doc in clicked_user]
                clicked_rate = 0
                if clicked_user:
                    clicked_rate = len(clicked_user) * 100 / len(campaign_users)
                unsubscribe_users =  mongo.db.campaign_users.find({"campaign":campaign['_id'],"unsubscribe_status" : True})
                unsubscribe_users = [serialize_doc(doc) for doc in unsubscribe_users]
                unsub = 0
                if unsubscribe_users:
                    unsub = len(unsubscribe_users) 
                campaign_update = mongo.db.campaigns.update({"_id": ObjectId(campaign['_id'])},{
                    "$set": {
                        "open_rate" : clicked_rate,
                        "seen_rate" : seen_rate,
                        "unsubscribed_users" : unsub
                    }
                })
            else:
                pass




