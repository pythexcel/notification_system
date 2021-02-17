
import requests

response = requests.get(
                            "https://isitarealemail.com/api/email/validate",
                            params = {'email':"xyz@excellencetechnologies.in"})
status = response.json()['status']  
print(status)
"""
import re
from email_validator import validate_email, EmailNotValidError
from dns import resolver 
import dns
import socket 
import smtplib
#def Emailvalidate(email_address):
    #Step 1: Check email
    #Check using Regex that an email meets minimum requirements, throw an error if not

addressToVerify = email_address
match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', addressToVerify)

#if match == None:
#    return False
#Step 2: Getting MX record
#Pull domain name from email address
domain_name = email_address.split('@')[1]

#get the MX record for the domain
records = dns.resolver.query(domain_name, 'MX')
mxRecord = records[0].exchange
mxRecord = str(mxRecord)

#Step 3: ping email server
#check if the email address exists

# Get local server hostname
host = socket.gethostname()

# SMTP lib setup (use debug level for full output)
server = smtplib.SMTP()
server.set_debuglevel(0)

# SMTP Conversation
server.connect(mxRecord)
server.helo(host)
server.mail(email_address)
code, message = server.rcpt(str(addressToVerify))
server.quit()

print(code)
# Assume 250 as Success

if code == 250:
    return True
else:
    return False
"""