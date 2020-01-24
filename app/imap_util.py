import imapclient
import pyzmail
import email
from app import mongo
from app.util import serialize_doc
import datetime
from app.mail_util import send_email
from bson.objectid import ObjectId
from app.config import bounced_mail_since,remind_mail_since

#Function for login with email_id and password all info fetching from db can set dynamically
def imap_login():
    mail_setting = mongo.db.mail_settings.find_one({"origin":"rase_tes","active":True})
    try:
        mail_username = mail_setting['mail_username']
        mail_password = mail_setting['mail_password']
        mail_server = mail_setting['mail_server']
        imapObj = imapclient.IMAPClient(mail_server, ssl=True)
        imapObj.login(mail_username,mail_password)
        return imapObj
    except Exception:
        return None


#cron for remind candidates if candidates not replied msg
def mail_reminder():
    imapObj =imap_login()       #calling imap login function 
    if imapObj is not None:
        all_mails_should_remind = []   
        imapObj.select_folder('[Gmail]/Sent Mail')   #fetching all UNANSWERED mails from a date we can set a date since we need all unanswered mail
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
                        except Exception:
                            pass
                        ret = mongo.db.recruit_mail.update({"_id":obj_id},{"$set":{"is_reminder" : False}}) #updating reminder status
                    else:
                        pass
                else:
                    pass
            else:
                pass
    else:
        pass

#cron for find bounced mails info
def bounced_mail():
    imapObj = imap_login()  #calling imap login function
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
                            "bounce_reason":reason
                        }},upsert=True)
            else:
                pass
    else:
        pass