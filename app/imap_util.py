import imapclient
import pyzmail
import email
import re
from app import mongo
from app.util import serialize_doc
import datetime
from app.mail_util import send_email
from bson.objectid import ObjectId
from app.config import bounced_mail_since,remind_mail_since



#cron for remind candidates if candidates not replied msg
def mail_reminder():
    mail_settings = mongo.db.imap_settings.find({"active":True})
    mail_settings = [serialize_doc(doc) for doc in mail_settings]
    for mail_setting in mail_settings:
        try:
            mail_username = mail_setting['mail_username']
            mail_password = mail_setting['mail_password']
            mail_server = mail_setting['mail_server']
            ssl = mail_setting['mail_use_ssl']
            folder = mail_setting['folder_name']
            imapObj = imapclient.IMAPClient(mail_server, ssl=ssl)
            imapObj.login(mail_username,mail_password)
        except Exception:
            imapObj = None
        if imapObj is not None:
            all_mails_should_remind = []
            imapObj.select_folder(folder)   #fetching all UNANSWERED mails from a date we can set a date since we need all unanswered mail
            ununswered_mails=imapObj.search(['SINCE',remind_mail_since,'UNANSWERED'])
            print(ununswered_mails)
            reminder_mails = mongo.db.recruit_mail.find({"is_reminder":True},{"_id":0,"to":1}) # fetching mails from db which should be remind that input we took at the time mail_send remind true or false
            reminder_mails = [doc for doc in reminder_mails]
            for reminder_mail in reminder_mails:
                mail = reminder_mail['to']
                all_mails_should_remind.append(mail)

            #here fetching unanswred mails info "from" "to" "subject" etc.
            for ununswered_mail in ununswered_mails:
                rawMessages = imapObj.fetch(ununswered_mail,['BODY[]'])
                message_body = pyzmail.PyzMessage.factory(rawMessages[ununswered_mail][b'BODY[]'])
                mail_subject = message_body.get_subject()
                mail_from =message_body.get_addresses('from')
                mail_to =message_body.get_addresses('to')
                if mail_to:
                    mails = mail_to[0][1]
                    if mails in all_mails_should_remind:  #In this condition checking if unanswered mail is of a candidate or anyone else 
                        reminder_mails = mongo.db.recruit_mail.find_one({"is_reminder":True,"to":mails,"subject":mail_subject})
                        if reminder_mails is not None:
                            obj_id = reminder_mails['_id']
                            message_str = reminder_mails['message']
                            subject = reminder_mails['subject']
                            to = [mails]
                            try:   #Sending same message as a reminder
                                send_email(message=message_str,recipients=to,subject=subject)
                                ret = mongo.db.recruit_mail.update({"_id":obj_id},{"$set":{"is_reminder" : False}}) #updating reminder status
                            except Exception:
                                ret = mongo.db.recruit_mail.update({"_id":obj_id},{"$set":{"is_reminder" : True}}) 
                        else:
                            pass
                    else:
                        pass
                else:
                    pass
        else:
            pass


#cron for find gmail bounced mails info
def bounced_mail():
    mail_settings = mongo.db.imap_settings.find({"active":True})
    mail_settings = [serialize_doc(doc) for doc in mail_settings]
    for mail_setting in mail_settings:
        try:
            mail_username = mail_setting['mail_username']
            mail_password = mail_setting['mail_password']
            mail_server = mail_setting['mail_server']
            ssl = mail_setting['mail_use_ssl']
            folder = mail_setting['folder_name']
            daemon_mail = mail_setting['daemon_mail']
            imapObj = imapclient.IMAPClient(mail_server, ssl=ssl)
            imapObj.login(mail_username,mail_password)
        except Exception:
            imapObj = None
        if imapObj is not None:
            imapObj.select_folder('INBOX')
            search_bounce_mails=imapObj.search(['SINCE',bounced_mail_since,'FROM',daemon_mail]) #searching bounced mails from a date
            soft_bounce_codes = ["421","450","451","452","520","521","522","531","545","553"] #these are soft bounce status codes
            hard_bounce_status = ["5.0.0","5.1.0","5.1.1","5.1.2","5.1.3","5.1.4","5.1.5","5.1.6","5.1.7","5.1.8","5.2.3","5.2.4","5.3.0","5.3.2","5.3.3","5.3.2","5.3.3","5.3.4","5.4.0","5.4.1","5.4.2","5.4.3","5.4.4","5.4.6","5.4.7","5.5.0","5.5.1","5.5.2","5.5.4","5.5.5","5.6.0","5.6.1","5.6.2","5.6.3","5.6.4","5.6.5","5.7.0","5.7.1","5.7.2","5.7.3","5.7.4","5.7.5","5.7.6","5.7.7"]
            soft_bounce_status = ["5.2.0","5.2.1","5.2.2","5.3.1","5.4.5","5.5.3"]
            for search_bounce_mail in search_bounce_mails:  #fetching bounced mail info from msg body
                rawMessages = imapObj.fetch(search_bounce_mail,['BODY[]'])
                message_body = pyzmail.PyzMessage.factory(rawMessages[search_bounce_mail][b'BODY[]'])
                mail_subject = message_body.get_subject()
                mail_from =message_body.get_addresses('from')
                mail_to =message_body.get_addresses('to')
                
                if message_body.text_part != None: #checking if msg body have text part
                    mail_text = message_body.text_part.get_payload().decode(message_body.text_part.charset)
                    match = re.search(r'[\w\.-]+@[\w\.-]+', mail_text)
                    bounced_mail = match.group(0)
                    regex = "xyz"
                    if regex in hard_bounce_status:
                        bounce_status = regex
                        bounce_type = "hard"
                    elif regex in soft_bounce_status:
                        bounce_status = regex
                        bounce_type = "soft"
                    else:
                        bounce_status = regex
                        bounce_type = None
                    ret = mongo.db.bounce_emails.update({ 
                            "bounced_mail": bounced_mail
                        }, {
                            "$set": {
                                "bounced_mail": bounced_mail,
                                "bounce_status":bounce_status,
                                "bounce_type":bounce_type
                            }},upsert=True)
                else:
                    pass
        else:
            pass


#cron for find gmail bounced mails info
def yahoo_bounced_mail(imapObj):
    if imapObj is not None:
        imapObj.select_folder('INBOX')
        search_bounce_mails=imapObj.search(['SINCE',bounced_mail_since,'FROM','mailer-daemon@yahoo.com']) #searching bounced mails from a date
        soft_bounce_codes = ["421","450","451","452","520","521","522","531","545","553"] #these are soft bounce status codes

        for search_bounce_mail in search_bounce_mails:  #fetching bounced mail info from msg body
            rawMessages = imapObj.fetch(search_bounce_mail,['BODY[]'])
            message_body = pyzmail.PyzMessage.factory(rawMessages[search_bounce_mail][b'BODY[]'])
            mail_subject = message_body.get_subject()
            mail_from =message_body.get_addresses('from')
            mail_to =message_body.get_addresses('to')
            
            if message_body.text_part != None: #checking if msg body have text part
                mail_text = message_body.text_part.get_payload().decode(message_body.text_part.charset)
                
                response_status = mail_text.split("we were unable to deliver your message to the following address.")  #spliting for checking reason msg. 
                string_code = response_status[1].split(": ")
                bounce_code = string_code[0] #checking for bounce code is hard bounce or soft bounce
                
                if bounce_code in soft_bounce_codes:
                    bounce_status = "soft_bounce"
                else:
                    bounce_status = "hard_bounce"
                mail_checker = response_status[1].split(">:")
                validate_mail = mail_checker[0].strip()
                bounced_mail = validate_mail[1:]
                reason = mail_checker[1].split("---")[0]

                ret = mongo.db.bounce_emails.update({ 
                        "bounced_mail": bounced_mail
                    }, {
                        "$set": {
                            "bounced_mail": bounced_mail,
                            "bounce_status":bounce_status,
                            "bounce_reason":reason,
                            "mail_type":"yahoo"
                        }},upsert=True)
            else:
                pass
    else:
        pass



#cron for find gmail bounced mails info
def gmail_bounced_mail(imapObj):
    if imapObj is not None:
        imapObj.select_folder('INBOX')
        search_bounce_mails=imapObj.search(['SINCE',bounced_mail_since,'FROM','mailer-daemon@googlemail.com']) #searching bounced mails from a date
        soft_bounce_codes = ["421","450","451","452","520","521","522","531","545","553"] #these are soft bounce status codes
        for search_bounce_mail in search_bounce_mails:  #fetching bounced mail info from msg body
            rawMessages = imapObj.fetch(search_bounce_mail,['BODY[]'])
            message_body = pyzmail.PyzMessage.factory(rawMessages[search_bounce_mail][b'BODY[]'])
            mail_subject = message_body.get_subject()
            mail_from =message_body.get_addresses('from')
            mail_to =message_body.get_addresses('to')
            if message_body.text_part != None: #checking if msg body have text part
                mail_text = message_body.text_part.get_payload().decode(message_body.text_part.charset)
                response_status = mail_text.split("The response was:")  #spliting for checking reason msg. 
                string_code = response_status[1].split(" ")
                bounce_code = string_code[0] #checking for bounce code is hard bounce or soft bounce
                if bounce_code in soft_bounce_codes:
                    bounce_status = "soft_bounce"
                else:
                    bounce_status = "hard_bounce"
                reason = response_status[1]
                mail_checker = mail_text.split("message wasn't delivered to ")
                validate_mail = mail_checker[1].split(" ")
                bounced_mail = validate_mail[0]  #getting bounced mail from mailer-daemon msg body
                #updating bounced mail info in db 
                ret = mongo.db.bounce_emails.update({ 
                        "bounced_mail": bounced_mail
                    }, {
                        "$set": {
                            "bounced_mail": bounced_mail,
                            "bounce_status":bounce_status,
                            "bounce_reason":reason,
                            "mail_type":"gmail"
                        }},upsert=True)
            else:
                pass
    else:
        pass



#cron for find gmail bounced mails info
def outlook_bounced_mail(imapObj):
    if imapObj is not None:
        imapObj.select_folder('INBOX')
        search_bounce_mails=imapObj.search(['SINCE',bounced_mail_since,'FROM','postmaster@outlook.com']) #searching bounced mails from a date
        soft_bounce_codes = ["421","450","451","452","520","521","522","531","545","553"] #these are soft bounce status codes
        for search_bounce_mail in search_bounce_mails:  #fetching bounced mail info from msg body
            rawMessages = imapObj.fetch(search_bounce_mail,['BODY[]'])
            message_body = pyzmail.PyzMessage.factory(rawMessages[search_bounce_mail][b'BODY[]'])
            mail_subject = message_body.get_subject()
            mail_from =message_body.get_addresses('from')
            mail_to =message_body.get_addresses('to')
            if message_body.text_part != None: #checking if msg body have text part
                mail_text = message_body.text_part.get_payload().decode(message_body.text_part.charset)
                response_status = mail_text.split("rejected your message to the following email addresses:")  #spliting for checking reason msg. 
                bounced_mail = response_status[1].split(" ")[0]
                msg_body = mail_text.split("Remote Server returned '")
                bounce_code = msg_body[1].split(" ")[0].split("-")[0]
                reason = msg_body[1].split("Original message headers:")[0]
                if bounce_code in soft_bounce_codes:
                    bounce_status = "soft_bounce"
                else:
                    bounce_status = "hard_bounce"
                mail_checker = mail_text.split("message wasn't delivered to ")
                print(bounced_mail)
                print(bounce_status)
                print(reason)
                ret = mongo.db.bounce_emails.update({ 
                        "bounced_mail": bounced_mail
                    }, {
                        "$set": {
                            "bounced_mail": bounced_mail,
                            "bounce_status":bounce_status,
                            "bounce_reason":reason,
                            "mail_type":"outlook"
                        }},upsert=True)
            else:
                pass
    else:
        pass