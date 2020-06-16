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
        response_data = json.loads(response.read().decode('utf-8'))#Here should be check if status in response_data else code will break here
        if response_data['status'] == "success":
            return True
        else:
            return False
    elif source == "twilio":
        account_sid = account_sid
        auth_token = auth_token
        client = Client(account_sid, auth_token)
        message = client.messages.create( body=message, from_= from_v, to=number)
        response = message.error_code
        if response == None:
            return True
        else:
            return False
    