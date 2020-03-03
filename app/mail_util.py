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
from bs4 import BeautifulSoup
from bson import ObjectId


def serialize_doc(doc):
    doc["_id"] = str(doc["_id"])
    return doc

def validate_smtp(username,password,port,smtp):
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

    
def validate_smtp_counts(ids):
    final_ids = []
    for id in ids:
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

def send_email(message,recipients,subject,bcc=None,cc=None,mail_from = None,filelink=None,filename=None,link=None,sending_mail=None,sending_password=None,sending_port=None,sending_server=None,user=None,digit=None,campaign_message_id=None,campaign=None,files=None):
    APP_ROOT = os.path.join(os.path.dirname(__file__), '..')
    dotenv_path = os.path.join(APP_ROOT, '.env')
    load_dotenv(dotenv_path)
    # again below checking origin condition as this function sends mail so need to check and select right smtp for single mail sending
    if os.getenv('origin') == "hr":
        mail_details = mongo.db.mail_settings.find_one({"origin": "HR"},{"_id":0})
    elif os.getenv('origin') == "recruit":    
        mail_details = mongo.db.mail_settings.find_one({"origin": "RECRUIT","active": True},{"_id":0})
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
        
    if mail_details is not None:
        if 'mail_from'in mail_details: 
            if mail_details['mail_from'] is not None:
                username = mail_details['mail_from']
    if mail_from is not None:
        username = mail_from

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = username
    msg['To'] = ','.join(recipients) 
    msg['Cc'] = cc

    if files is not None:
        for f in files:
            file_path = open(f['file'],'rb')
            attachment = email.mime.application.MIMEApplication(file_path.read())
            file_path.close()
            attachment.add_header('Content-Disposition','attachment', filename=f['file_name'])
            msg.attach(attachment)
    else:
        pass

    if filelink is not None:
        fo=open(filelink,'rb')
        file = email.mime.application.MIMEApplication(fo.read())
        fo.close()
        file.add_header('Content-Disposition','attachment',filename=filename)
        msg.attach(file)
    else:
        pass

    if user is not None:
        url = "<img src= '{}template_hit_rate/{}/{}/{}?hit_rate=1' hidden=true>".format(base_url,digit,campaign_message_id,user)
        soup = BeautifulSoup(message,"lxml")
        for data in soup.find_all('a', href=True):
            required_url = data['href'].split("?")
            if len(required_url) == 1: 
                message = message.replace(required_url[0],base_url+'campaign_redirect/'+ '{}/{}?url={}'.format(digit,campaign,required_url[0]) )
            else:
                message = message.replace(required_url[0],base_url+'campaign_redirect/'+ '{}/{}'.format(digit,campaign))
        message = message + url 
    main = MIMEText(message,'html')
    msg.attach(main)
    mail.sendmail(username,delivered, msg.as_string()) 
    mail.quit()
    
