import requests
from app import mongo
import smtplib    


def send_email(message,recipients,subject,bcc=None,cc=None):
    # fetching mail details
    mail_details = mongo.db.mail_settings.find_one({},{"_id":0})
    username = mail_details["MAIL_USERNAME"]
    password = mail_details["MAIL_PASSWORD"]
    port = mail_details['MAIL_PORT']
    mail_server = mail_details['MAIL_SERVER']
    # sending mail from smtp
    mail = smtplib.SMTP_SSL(str(mail_server), port)
    mail.login(username,password)
    message = 'Subject: {}\n\n{}'.format(subject, message)
    mail.sendmail(username,recipients, message) 
    mail.quit()
    
    
    
    
    
    
    
    
    
    
    
