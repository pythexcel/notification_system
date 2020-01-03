import requests
from app import mongo
import smtplib    
import os 
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import email.mime.application
import mimetypes
# <img src='http://176.9.137.77:8007/template_hit_rate?template=5e005c0f44f73ecd868cb8c5&hit_rate=1' style='display:none'/>

def send_email(message,recipients,subject,bcc=None,cc=None,filelink=None,filename=None):
    mail_details = mongo.db.mail_settings.find_one({},{"_id":0})
    username = mail_details["mail_username"]
    password = mail_details["mail_password"]
    port = mail_details['mail_port']
    mail_server = mail_details['mail_server']
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
    main = MIMEText(message,'html')
    msg.attach(main)
    mail.sendmail(username,delivered, msg.as_string()) 
    mail.quit()
    