#from app import mongo
from app.util.serializer import serialize_doc
import datetime
import dateutil.parser
from bson.objectid import ObjectId
from app.utils import fetching_validated_account
from app.account import initDB


def calculate_bounce_rate():
    accounts,account_config = fetching_validated_account()
    for account in accounts:  
        account_mongo = account_config[account]
        mongo = initDB(account,account_mongo)  
        campaigns = mongo.campaigns.find({})
        campaigns = [serialize_doc(doc) for doc in campaigns]
        
        for campaign in campaigns:
            if campaign is not None:
                campaign_users = mongo.campaign_users.find({"campaign":campaign['_id']})
                campaign_users = [serialize_doc(doc) for doc in campaign_users]
                bounce_users = mongo.mail_status.find({"campaign":campaign['_id'],"bounce": True,"bounce_type":"hard"})
                bounce_users = [serialize_doc(doc) for doc in bounce_users]
                total_users = len(campaign_users)
                if total_users != 0:
                    bounce_rate = len(bounce_users) * 100 / total_users
                    campaign = mongo.campaigns.update({"_id": ObjectId(campaign['_id'])},{
                        "$set": {
                            "bounce_rate": bounce_rate
                        }
                    })
                else:
                    pass
            else:
                pass
