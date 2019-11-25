from app import mongo
import requests
from flask import jsonify
import datetime
from pyfcm import FCMNotification
from app.config import fcm_api_key


def Push_notification(fcm_registration_id=None,message=None,subject=None):
    push_service = FCMNotification(api_key=fcm_api_key)
    registration_id = fcm_registration_id
    message_title = subject
    message_body = message
    result = push_service.notify_single_device(registration_id=registration_id, message_title=message_title, message_body=message_body)
    print(result)

