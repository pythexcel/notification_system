import json
import os
import requests
import datetime
import urllib.request
import urllib.parse
from flask import jsonify
from app.config import fcm_api_key
from dotenv import load_dotenv
from twilio.rest import Client
from pyfcm import FCMNotification

APP_ROOT = os.path.join(os.path.dirname(__file__), '..')
dotenv_path = os.path.join(APP_ROOT, '.env')
load_dotenv(dotenv_path)


def create_sms( phone=None, mobile_message_str=None ):
    phone_status = False
    phone_issue = False
    phone_issue_message = None
    try:
        if os.getenv('service') == "textlocal":
            req_sms = dispatch_sms(source="textlocal",apikey=os.getenv('localtextkey'),number=phone,message=mobile_message_str)
            phone_status = req_sms
        elif os.getenv('service') == "twilio":
            req_sms = dispatch_sms(source="twilio",auth_token = os.getenv('twilioToken'),account_sid = os.getenv('twilioSid'),number=phone,message=mobile_message_str,from_v= os.getenv('twilio_number'))
            phone_status = req_sms
        return phone_status,phone_issue,phone_issue_message
    except Exception as error:
        phone_issue_message = str(error)
        phone_status = False
        phone_issue = True
        return phone_status,phone_issue,phone_issue_message


def dispatch_sms( message, number, source, apikey = None, from_v = None, auth_token = None, account_sid = None ):
    if source == "textlocal":
        data =  urllib.parse.urlencode({'apikey': apikey , 'numbers': number,'message' : message})
        data = data.encode('utf-8')
        request_api = urllib.request.Request("https://api.textlocal.in/send/?")
        response = urllib.request.urlopen(request_api, data)
        response_data = json.loads(response.read().decode('utf-8'))
        if response_data['status'] == "success":
            return True
        else:
            return False
    elif source == "twilio":
        account_sid = account_sid
        auth_token = auth_token
        client = Client(account_sid, auth_token)
        message = client.messages.create( body=message, from_= from_v, to=number)
        response = message.sid
        if response['error_code'] == None:
            return True
        else:
            return False