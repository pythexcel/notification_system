from app import mongo
from dotenv import load_dotenv
import smtplib,ssl    
import os 
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import email.mime.application
import mimetypes
from app.config import smtp_counts,base_url,default_unsub
import uuid
from bs4 import BeautifulSoup
from bson import ObjectId
import re
from app.util.serializer import serialize_doc
import datetime



def send_email(message,recipients,subject,sender_name=None,bcc=None,cc=None,mail_from = None,filelink=None,filename=None,link=None,sending_mail=None,sending_password=None,sending_port=None,sending_server=None,user=None,digit=None,campaign_message_id=None,campaign=None,files=None):
    APP_ROOT = os.path.join(os.path.dirname(__file__), '..')
    dotenv_path = os.path.join(APP_ROOT, '.env')
    load_dotenv(dotenv_path)
    if "pytest" in sys.modules:
        mail_details = mongo.db.mail_settings.find_one({"origin": "CAMPAIGN"},{"_id":0})
    else:
        # again below checking origin condition as this function sends mail so need to check and select right smtp for single mail sending
        if os.getenv('origin') == "hr":
            mail_details = mongo.db.mail_settings.find_one({"origin": "HR"},{"_id":0})
        elif os.getenv('origin') == "recruit":    
            mail_details = mongo.db.mail_settings.find_one({"origin": "RECRUIT","active": True},{"_id":0})
        elif os.getenv('origin') == "tms":    
            mail_details = mongo.db.mail_settings.find_one({"origin": "TMS","active": True},{"_id":0})

    if mail_details is None:
        mail_details = {"mail_server":"smtp.sendgrid.net","mail_port":587,"origin":"RECRUIT","mail_use_tls":True,"mail_username":"apikey","mail_password":os.getenv('send_grid_key'),"active":True,"type":"tls","mail_from":"noreply@excellencetechnologies.in"}
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
    from email.header import Header
    from email.utils import formataddr
    if sender_name is not None:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = formataddr((str(Header(str(sender_name), 'utf-8')), username))
        msg['To'] = ','.join(recipients) 
        msg['Cc'] = cc
    else:
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
        unsuscribe_url =  default_unsub.format(base_url,delivered[0],campaign)
        url = "<img src= '{}template_hit_rate/{}/{}/{}?hit_rate=1' hidden=true>".format(base_url,digit,campaign_message_id,user)
        soup = BeautifulSoup(message,"lxml")
        for data in soup.find_all('a', href=True):
            required_url = data['href'].split("?")
            if len(required_url) == 1: 
                message = message.replace(required_url[0],base_url+'campaign_redirect/'+ '{}/{}?url={}'.format(digit,campaign,required_url[0]) )
            else:
                message = message.replace(required_url[0],base_url+'campaign_redirect/'+ '{}/{}'.format(digit,campaign))
        
        unsub_expression = re.compile('#unsub')
        unsub_exist = False
        if re.search(unsub_expression, message):
            rexWithString = '#' + re.escape('unsub')
            message = re.sub(rexWithString, "<a href='{}unsubscribe_mail/{}/{}'>Unsubscribe</a>".format(base_url,delivered[0],campaign),message)
            unsub_exist = True
        if unsub_exist:
            message = message + url 
        else:
            message = message + url + unsuscribe_url 
            
    main = MIMEText(message,'html')
    msg.attach(main)
    mail.sendmail(username,delivered, msg.as_string()) 
    mail.quit()
