import json
import urllib.request
import urllib.parse
from twilio.rest import Client


def dispatch_sms(message, number, source, apikey = None, from_v = None, auth_token = None, account_sid = None):
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
    