import requests
from app import mongo
from flask_mail import Message,Mail
from app import mail
from flask import current_app   



def send_email(email,message,sender,subject,bcc,cc): 
    app = current_app._get_current_object()
    cc = [cc,]
    bcc = [bcc,]
    message = message
    subject = subject
    sender = sender
    recipient = [email,] + cc + bcc
    msg = Message(message,sender=sender,recipients=recipient)
    mail.send(msg)