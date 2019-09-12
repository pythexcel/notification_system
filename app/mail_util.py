import requests
from app import mongo
import smtplib    


def send_email(message,recipients,subject,bcc=None,cc=None):
    # fetching mail details
    mail_details = mongo.db.mail_settings.find_one({},{"_id":0})
    username = mail_details["mail_username"]
    password = mail_details["mail_password"]
    port = mail_details['mail_port']
    mail_server = mail_details['mail_server']
    # sending mail from smtp
    mail = smtplib.SMTP_SSL(str(mail_server), port)
    mail.login(username,password)
    message = 'Subject: {}\n\n{}'.format(subject, message)
    mail.sendmail(username,recipients, message) 
    mail.quit()
    
    
    
    
    
    
    
    
    
    
    
