

from flask import current_app as app
import re
#from app import mongo
from flask import jsonify
import datetime


def interview_rejection(req,message_str,message_subject,smtp_email):
    reject_mail = None
    if "sender_name" in req:
        sender_name = req['sender_name']
    else:
        sender_name = None
    if app.config['ENV'] == 'production':
        if 'email' in req['data']:
            reject_mail = req['data']['email']
        else:
            return False
            #return jsonify({"status": False,"Message": "No rejection mail is sended"}), 400
    else:
        if app.config['ENV'] == 'development':
            email = req['data']['email']
            full_domain = re.search("@[\w.]+", email)  
            domain = full_domain.group().split(".")
            if domain[0] == "@excellencetechnologies":
                reject_mail = email
            else:
                reject_mail = app.config['to']   
    reject_handling = mongo.db.rejection_handling.insert_one({
                    "email": reject_mail,
                    'rejection_time': req['data']['rejection_time'],
                    'send_status': False,
                    'message': message_str,
                    'subject': message_subject,
                    'sender_name':sender_name,
                    'smtp_email': smtp_email
            }).inserted_id  
    return True
    #return jsonify({"status":True,"*Note":"Added for Rejection"}),200



def interview_reminder_set(req,message_str,message_subject,smtp_email):
    jobId = req.get('jobId')
    date = datetime.datetime.now()
    message_key = "Interview Reminder"
    if jobId is not None:
        reject_handling = mongo.db.reminder_details.insert_one({
                    "jobId": jobId,
                    'date': date,
                    'message_key': message_key
            }).inserted_id 
        return True
    else:
        return False