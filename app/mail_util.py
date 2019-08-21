import requests
from app import mongo
from app.config import mail_settings
from flask_mail import Message,Mail
from app import mail
from flask import current_app   



def send_email(email,message,sender): 
    app = current_app._get_current_object()
    message = message
    sender = sender
    recipient = [email,]
    msg = Message(message,sender=sender,recipients=recipient)
    mail.send(msg)