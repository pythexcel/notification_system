import imapclient
import pyzmail
import email
import datetime
import re
from app.util import serialize_doc
from app.mail_util import send_email
from bson.objectid import ObjectId
from app.config import hard_bounce_status,soft_bounce_status
from app import mongo
from datetime import date


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

def bounced_mail():
    mail_settings = mongo.db.mail_settings.find({"origin": "CAMPAIGN"})
    mail_settings = [serialize_doc(doc) for doc in mail_settings]
    for mail_setting in mail_settings:
        mail_username = mail_setting['mail_username']
        mail_password = mail_setting['mail_password']
        mail_server = mail_setting['mail_server']
        daemon_mail = mail_setting['daemon_mail']
        imapObj = imapclient.IMAPClient(mail_server, ssl=True)
        imapObj.login(mail_username,mail_password)
        if imapObj is not None:
            imapObj.select_folder('INBOX')
            bounced_mail_date = datetime.datetime.today()
            bounced_mail_since = "{}-{}-{}".format(bounced_mail_date.strftime("%d"),bounced_mail_date.strftime("%b"),bounced_mail_date.strftime("%Y"))
            search_bounce_mails=imapObj.search(['SINCE',bounced_mail_since,'FROM',daemon_mail]) #searching bounced mails from a date
            for search_bounce_mail in search_bounce_mails:
               #fetching bounced mail info from msg body
                rawMessages = imapObj.fetch(search_bounce_mail,['BODY[]'])
                message_body = pyzmail.PyzMessage.factory(rawMessages[search_bounce_mail][b'BODY[]'])
                mail_subject = message_body.get_subject()
                mail_from =message_body.get_addresses('from')
                mail_to =message_body.get_addresses('to')
                if message_body.text_part != None:
                    #checking if msg body have text part
                    mail_text = message_body.text_part.get_payload().decode(message_body.text_part.charset)
                    match = re.search(r'[\w\.-]+@[\w\.-]+', mail_text)
                    bounced_mail = match.group(0)
                    bounce_codes = re.findall(r"(5\.[0-9].[0-9])", mail_text)
                    bounce_status = None
                    bounce_type = "hard"
                    for bounce_code in bounce_codes:
                        if bounce_code in hard_bounce_status:
                            bounce_status = bounce_code
                            bounce_type = "hard"
                            break
                        if bounce_code in soft_bounce_status:
                            bounce_status = bounce_code
                            bounce_type = "soft"
                            break
                    dt = date.today()
                    sendDate = datetime.datetime.combine(dt,datetime.datetime.min.time())
                    ret = mongo.db.mail_status.update({
                            "user_mail": bounced_mail,
                            "sending_time": {"$gte": sendDate}
                        }, {
                            "$set": {
                                "bounce": True,
                                "bounce_status":bounce_status,
                                "bounce_type":bounce_type
                            }})
                else:
                    pass
        else:
            pass