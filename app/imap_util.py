import imapclient
import pyzmail
import email
from app import mongo
from app.util import serialize_doc
import datetime
from app.mail_util import send_email
from bson.objectid import ObjectId
from app.config import bounced_mail_since,remind_mail_since



#cron for remind candidates if candidates not replied msg
def mail_reminder():
    all_origin = ["test_gmail","test_outlook","test_yahoo"]
    for origin in all_origin:
        mail_setting = mongo.db.mail_settings.find_one({"origin":origin,"active":True})
        try:
            mail_username = mail_setting['mail_username']
            mail_password = mail_setting['mail_password']
            mail_server = mail_setting['mail_server']
            imapObj = imapclient.IMAPClient(mail_server, ssl=True)
            imapObj.login(mail_username,mail_password)
        except Exception:
            imapObj = None
        if imapObj is not None:
            all_mails_should_remind = []
            if origin == "test_gmail":
                imapObj.select_folder('[Gmail]/Sent Mail')   #fetching all UNANSWERED mails from a date we can set a date since we need all unanswered mail
            else:
                imapObj.select_folder(b'Sent')
            ununswered_mails=imapObj.search(['SINCE',remind_mail_since,'UNANSWERED'])
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
    all_origin = ["test_gmail","test_outlook","test_yahoo"]
    for origin in all_origin:
        mail_setting = mongo.db.mail_settings.find_one({"origin":origin,"active":True})
        try:
            mail_username = mail_setting['mail_username']
            mail_password = mail_setting['mail_password']
            mail_server = mail_setting['mail_server']
            imapObj = imapclient.IMAPClient(mail_server, ssl=True)
            imapObj.login(mail_username,mail_password)
        except Exception:
            imapObj = None
        if imapObj is not None:
            if origin == "test_gmail":
                gmail_bounced_mail(imapObj)
            if origin == "test_outlook":
                outlook_bounced_mail(imapObj)
            if origin == "test_yahoo":
                yahoo_bounced_mail(imapObj)
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