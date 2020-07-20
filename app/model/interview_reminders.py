from app import mongo
from app.util.serializer import serialize_doc

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
