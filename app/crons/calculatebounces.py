from app import mongo
from app.util.serializer import serialize_doc
import datetime
import dateutil.parser
from bson.objectid import ObjectId



def calculate_bounce_rate():
    campaigns = mongo.db.campaigns.find({})
    campaigns = [serialize_doc(doc) for doc in campaigns]
    
    for campaign in campaigns:
        if campaign is not None:
            campaign_users = mongo.db.campaign_users.find({"campaign":campaign['_id']})
            campaign_users = [serialize_doc(doc) for doc in campaign_users]
            bounce_users = mongo.db.mail_status.find({"campaign":campaign['_id'],"bounce": True,"bounce_type":"hard"})
            bounce_users = [serialize_doc(doc) for doc in bounce_users]
            total_users = len(campaign_users)
            if total_users != 0:
                bounce_rate = len(bounce_users) * 100 / total_users
                campaign = mongo.db.campaigns.update({"_id": ObjectId(campaign['_id'])},{
                    "$set": {
                        "bounce_rate": bounce_rate
                    }
                })
            else:
                pass
        else:
            pass
