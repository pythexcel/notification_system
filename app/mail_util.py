import requests
from app import mongo
from flask_mail import Message,Mail
from app import mail
from flask import current_app   



def send_email(email,message,sender,subject,bcc,cc):
    # this is loading the flask in build config file to get smtp details 
    app = current_app._get_current_object()
    cc = [cc,]
    bcc = [bcc,]
    # here getting message which is constructed
    message = message
    # here subject of that message
    subject = subject
    # here getting sender mail which is sending the mail or from smtp details user
    sender = sender
    # here email which will recieve mail can be send to multipl
    recipient = [email,] + cc + bcc
    # here message  is constructed for mail with required parameters
    msg = Message(message,subject=subject,sender=sender,recipients=recipient)
    # Here mail in sended 
    mail.send(msg)