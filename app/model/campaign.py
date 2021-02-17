from app import mongo
from app.util.serializer import serialize_doc
from bson.objectid import ObjectId


def user_data(campaign_details):
    details = mongo.db.campaign_users.find({"campaign":campaign_details['_id']})
    details = [serialize_doc(doc) for doc in details]
    
    for data in details:
        hit_data = []
        if 'mail_message' in data:
            for element in data['mail_message']:
                if element['campaign'] == campaign_details['_id']:
                    hit_details = mongo.db.mail_status.find_one({"digit": element['sended_message_details']},
                    {
                        "hit_rate":1,
                        "message":1,
                        "mail_sended_status":1,
                        "seen_date":1,
                        "sending_time": 1,
                        "subject": 1,
                        "seen": 1 ,
                        "clicked": 1,
                        "bounce": 1,
                        "bounce_type" : 1
                    })
                    if hit_details is not None:
                        hit_details['_id'] = str(hit_details['_id'])
                        if hit_details not in hit_data:
                            hit_data.append(hit_details)
        data['hit_details'] = hit_data
        data['mail_message'] = None
    campaign_details['users'] = details
    varificationstatus = mongo.db.campaigns.find_one({"_id": ObjectId(campaign_details['_id'])})
    status = "Stop"
    if varificationstatus:
        if "verification" in varificationstatus:
            status = varificationstatus['verification']
        
    validate = mongo.db.campaign_clicked.find({"campaign_id": campaign_details['_id']})
    if validate:
        clicking_details = mongo.db.campaign_clicked.aggregate([
            {
            "$project": 
            {   "clicked_time": 1,
                "campaign_id": 1,
                "month": { "$month": "$clicked_time" },
                "day": { "$dayOfMonth": "$clicked_time" },
                "time":{
                "$switch":
                {
                "branches": [
                    {
                    "case": { "$and" : [ { "$gte" : [ {  "$hour" : "$clicked_time" },0 ] },
                                    { "$lt" : [ { "$hour" : "$clicked_time" },6 ] } ] },
                    "then": "morning"
                    },
                    {
                    "case": { "$and" : [ { "$gte" : [ {  "$hour" : "$clicked_time" },6 ] },
                                    { "$lt" : [ { "$hour" : "$clicked_time" },12 ] } ] },
                    "then": "noon"
                    },
                    {
                    "case": { "$and" : [ { "$gte" : [ {  "$hour" : "$clicked_time" },12 ] },
                                    { "$lt" : [ { "$hour" : "$clicked_time" },18 ] } ] },
                    "then": "evening"
                    },
                    {
                    "case": { "$and" : [ { "$gte" : [ {  "$hour" : "$clicked_time" },18 ] },
                                    { "$lt" : [ { "$hour" : "$clicked_time" },24 ] } ] },
                    "then": "night"
                    }
                ],
                "default": "No record found."
                } 
                }}},
                {
                "$match": {"campaign_id": campaign_details['_id']}
                },
                { "$group": { "_id": {"interval":"$time","month":"$month","day":"$day"}, "myCount": { "$sum": 1 },"clicking_date" : {"$first": "$clicked_time"} } },
                { "$sort" : { "clicking_date" : -1 } }
                ])
        clicking_data = []
        currDate = None
        currMonth = None
        for data in clicking_details:
            if currDate is None or (currMonth != data['_id']['month'] and currDate == data['_id']['day']) or (currDate != data['_id']['day']):
                clicking_data.append({'date': data['clicking_date'], data['_id']['interval']: data['myCount'] })
            else:
                clicking_data[-1][data['_id']['interval']] = data['myCount']
            currMonth = data['_id']['month']
            currDate = data['_id']['day']
        campaign_details['clicking_details'] = clicking_data
    else:
        campaign_details['clicking_details'] = []
    campaign_details['verification'] = status
    return campaign_details


def campaign_details(user):
    name = user['campaign']
    ret = mongo.db.campaigns.find_one({"_id": ObjectId(name)})
    if ret is not None:
        user['campaign'] = serialize_doc(ret)
    else:
        user['campaign'] = None
    return user   
