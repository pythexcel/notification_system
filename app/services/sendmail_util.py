import os 
import re
import uuid
import datetime
import requests
import smtplib,ssl    
import mimetypes
import email.mime.application
from app import mongo
from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from app.config import base_url, default_unsubscribe_html
from bs4 import BeautifulSoup


def create_sender_list( request, details ):
    APP_ROOT = os.path.join(os.path.dirname(__file__), '..')
    dotenv_path = os.path.join(APP_ROOT, '.env')
    load_dotenv(dotenv_path)
    to = None
    bcc = None
    cc = None
    current_environment = os.getenv('ENVIRONMENT')
    if current_environment == "development":
        if 'to' in request:
            for email in request.get('to'):
                full_domain = re.search("@[\w.]+", email)  
                domain = full_domain.group().split(".")
                if domain[0] == "@excellencetechnologies":
                    to = [email]
                else:
                    to = [os.getenv('to')]
        bcc = [os.getenv('bcc')]
        cc = [os.getenv('cc')]

    else:
        if current_environment == 'production':
            if 'to' in request:
                if not request.get('to'):
                    to = None
                else:     
                    to = request.get('to')
            else:
                to = None
            if 'bcc' in request:    
                if not request.get('bcc'):
                    bcc = None
                else:
                    bcc = request.get('bcc')
            else:
                bcc = None
            
            if 'cc' in request: 
                if not request.get('cc'):
                    cc = None
                else:
                    cc = request.get('cc')
            else:        
                cc = None
    if to is None:
        return { 'mailing_staus': False }
    else:
        mail_list = {
            "to": to,
            "bcc" bcc,
            "cc": cc
        }
        return dispatch_mail( sending_mail_list= mail_list, details= details)


def dispatch_mail( sending_mail_list, details ):
    smtp_email = details.get('smtp_email')
    if smtp_email is not None:
        smtp_details = mongo.db.mail_settings.find_one({ "mail_username": smtp_email }, { "_id": 0 })
        if smtp_details is not None:
            details['username'] = smtp_details['mail_username']
            details['password'] = smtp_details['mail_password']
            details['port'] = smtp_details['mail_port']
            details['smtp_server'] = smtp_details['mail_server']
            details['mail_from'] = None
            if 'mail_from' in smtp_details:
                details['mail_from'] = smtp_details['mail_from']
        else:
            raise Exception('No smtp conf avialable with the provide smtp email')
    else:
        smtp_details = mongo.db.mail_settings.find_one({}, { "_id": 0 })
        if smtp_details is not None:
            details['username'] = smtp_details['mail_username']
            details['password'] = smtp_details['mail_password']
            details['port'] = smtp_details['mail_port']
            details['smtp_server'] = smtp_details['mail_server']
            details['mail_from'] = None
            if 'mail_from' in smtp_details:
                details['mail_from'] = smtp_details['mail_from']
        else:
            raise Exception('No smtp conf avialable in the system currently')
    send_email( email_list=sending_mail_list, details=details )
    return { 'message': 'mail_sended'}


def send_email( email_list, details ):
    recipients = sending_mail_list.get('to')
    bcc = sending_mail_list.get('bcc')
    cc = sending_mail_list.get('cc')
    filelink = details.get('single_filelink')
    filename = details.get('single_filelink')
    message = details.get('message')
    subject = details.get('subject')
    files = details.get('files')
    user = details.get('user')
    digit = details.get('digit')
    campaign_message_id = details.get('campaign_message_id')
    campaign = details.get('campaign')
    username = details.get('username')
    password = details.get('password')
    port = details.get('port')
    mail_server = details.get('mail_server')
    mail_from = details.get('mail_from')
  
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
        
    if mail_from is not None:
        username = mail_from

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = username
    msg['To'] = ','.join(recipients) 
    msg['Cc'] = cc

    if files is not None:
        for file_detail in files:
            file_path = open(file_detail['file'],'rb')
            attachment = email.mime.application.MIMEApplication(file_path.read())
            file_path.close()
            attachment.add_header('Content-Disposition','attachment', filename=file_detail['file_name'])
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
    
