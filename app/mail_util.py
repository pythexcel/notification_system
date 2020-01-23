import datetime
import requests
from app import mongo
from dotenv import load_dotenv
import smtplib,ssl    
import os 
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import email.mime.application
import mimetypes
from app.config import smtp_counts,base_url
import uuid

def serialize_doc(doc):
    doc["_id"] = str(doc["_id"])
    return doc

def validate_smtp_counts():
    mail = mongo.db.mail_settings.find({"origin": "CAMPAIGN","current_working_status":True}).sort("priority",1)
    mail = [serialize_doc(doc)for doc in mail]
    valid_smtp = []
    for data in mail:
        mail_username = data['mail_username']
        mail_password = data['mail_password']
        mail_smtp = data['mail_server']
        mail_port = data['mail_port']
        if mail_smtp in smtp_counts:
            # here below is the condtions we will check for smtp counts and values 
            today = datetime.datetime.today()
            next_day = datetime.datetime.today() + datetime.timedelta(days=1)
            smtp_validate = mongo.db.smtp_count_validate.find_one({"smtp":mail_smtp,"email":mail_username,
            "created_at":{
            "$gte": datetime.datetime(today.year, today.month, today.day),
            "$lte": datetime.datetime(next_day.year, next_day.month, next_day.day)}})
            if smtp_validate is not None:
                if smtp_validate['count'] < smtp_counts[mail_smtp]:
                    valid_smtp.append({
                        "mail_username":mail_username,
                        "mail_password":mail_password,
                        "mail_server":mail_smtp,
                        "mail_port":mail_port,
                        "count_details":str(smtp_validate['_id'])})
                    return valid_smtp
            else:
                smtp_validate_insert = mongo.db.smtp_count_validate.insert_one({
                    "smtp":mail_smtp,
                    "email":mail_username,
                    "created_at": today,
                    "count": 0
                }).inserted_id
                valid_smtp.append({
                    "mail_username":mail_username,
                    "mail_password":mail_password,
                    "mail_server":mail_smtp,
                    "mail_port":mail_port,
                    "count_details":str(smtp_validate_insert)})      
                return valid_smtp


def send_email(message,recipients,subject,bcc=None,cc=None,filelink=None,filename=None,link=None,sending_mail=None,sending_password=None,sending_port=None,sending_server=None,template_id=None,user=None,digit=None):
    APP_ROOT = os.path.join(os.path.dirname(__file__), '..')
    dotenv_path = os.path.join(APP_ROOT, '.env')
    load_dotenv(dotenv_path)
    # again below checking origin condition as this function sends mail so need to check and select right smtp for single mail sending
    if os.getenv('origin') == "hr":
        mail_details = mongo.db.mail_settings.find_one({"origin": "HR"},{"_id":0})
    elif os.getenv('origin') == "recruit":    
        mail_details = mongo.db.mail_settings.find_one({"origin": "RECRUIT"},{"_id":0})
    username = None
    if sending_mail is None:    
        username = mail_details["mail_username"]
    else:
        username = sending_mail 
    password = None
    #below is written for recruit condition for multiple smtp as need to iterate over values from campaign schduler
    if sending_password is None:       
        password = mail_details["mail_password"]
    else:
        password = sending_password   
    if sending_port is None:        
        port = mail_details['mail_port']
    else:
        port = sending_port
    if sending_server is None:        
        mail_server = mail_details['mail_server']
    else:
        mail_server = sending_server  
    context = ssl.create_default_context() 
    if port == 587:       
        mail = smtplib.SMTP(str(mail_server), port)
        mail.ehlo() 
        mail.starttls(context=context) 
        mail.ehlo() 
        mail.login(username,password)
    else:
        mail = smtplib.SMTP_SSL(str(mail_server), port)
        mail.login(username,password)
    delivered = []
    for element in recipients:
        delivered.append(element)
    if bcc is not None:
        for data in bcc:
            delivered.append(data) 
    else:
        bcc = None
    if cc is not None:
        for data in cc:
            delivered.append(data)
        cc =  ','.join(cc)
    else:
        cc = None
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = username
    msg['To'] = ','.join(recipients) 
    msg['Cc'] = cc
    if filelink is not None:
        fo=open(filelink,'rb')
        file = email.mime.application.MIMEApplication(fo.read())
        fo.close()
        file.add_header('Content-Disposition','attachment',filename=filename)
        msg.attach(file)
    else:
        pass
    if template_id is not None:
        if user is not None:
            url = "<img src= '{}template_hit_rate/{}/{}?template={}&hit_rate=1'>".format(base_url,digit,user,template_id)
            url_create = message.split("href=")
            for data in url_create:
                data = data.split("/?")
                message = message.replace(data[0][1:],base_url+'campaign_redirect/'+ '{}'.format(digit))
            message = message + url 
    main = MIMEText(message,'html')
    msg.attach(main)
    mail.sendmail(username,delivered, msg.as_string()) 
    mail.quit()
    