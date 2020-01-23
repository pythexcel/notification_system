import re
from app import mongo
from app.util import serialize_doc
import datetime
import dateutil.parser
from bson.objectid import ObjectId
from app.mail_util import send_email
from app.slack_util import slack_message
from flask import current_app as app
import imapclient
import pyzmail
import email


def campaign_mail():
    ret = mongo.db.campaign_users.find_one({"send_status":False})
    if ret is not None:
        if app.config['ENVIRONMENT'] == "development":
            mail = "recruit_testing@mailinator.com"
        else:
            mail = ret['email']
        cam = mongo.db.campaigns.find_one({"_id":ObjectId(ret['campaign'])})
        if cam is not None:
            if 'Template' in cam:
                for data in cam['Template']:
                    system_variable = mongo.db.mail_variables.find({})
                    system_variable = [serialize_doc(doc) for doc in system_variable]
                    temp = mongo.db.mail_template.find_one({"_id":ObjectId(data)})
                    subject = temp['message_subject']
                    message_variables = []
                    message = temp['message'].split('#')
                    del message[0]
                    rex = re.compile('!|@|\$|\%|\^|\&|\*|\:|\;')
                    for elem in message:
                        varb = re.split(rex, elem)
                        message_variables.append(varb[0])
                    message_str = temp['message']
                    for detail in message_variables:
                        if detail in ret:
                            rexWithString = '#' + re.escape(detail) + r'([!]|[@]|[\$]|[\%]|[\^]|[\&]|[\*]|[\:]|[\;])'
                            message_str = re.sub(rexWithString, ret[detail], message_str)
                        else:
                            for element in system_variable:
                                if "#" + detail == element['name'] and element['value'] is not None:
                                    rexWithSystem = re.escape(element['name']) + r'([!]|[@]|[\$]|[\%]|[\^]|[\&]|[\*]|[\:]|[\;])' 
                                    message_str = re.sub(rexWithSystem, element['value'], message_str)  

                    subject_variables = []
                    message_sub = subject.split('#')
                    del message_sub[0]
                    regex = re.compile('!|@|\$|\%|\^|\&|\*|\:|\;')
                    for elem in message_sub:
                        sub_varb = re.split(regex, elem)
                        subject_variables.append(sub_varb[0])
                    message_subject = subject
                    for detail in subject_variables:
                        if detail in ret:
                            rexWithString = '#' + re.escape(detail) + r'([!]|[@]|[\$]|[\%]|[\^]|[\&]|[\*]|[\:]|[\;])'
                            message_subject = re.sub(rexWithString, ret[detail], message_subject)
                        else:
                            for element in system_variable:
                                if "#" + detail == element['name'] and element['value'] is not None:
                                    rexWithSystem = re.escape(element['name']) + r'([!]|[@]|[\$]|[\%]|[\^]|[\&]|[\*]|[\:]|[\;])' 
                                    message_subject = re.sub(rexWithSystem, element['value'], message_subject)  



                    to = []
                    to.append(mail)
                    working_status = True
                    try:        
                        send_email(message=message_str,recipients=to,subject=subject)
                    except Exception:
                        working_status = False
                    mail_data = mongo.db.mail_status.insert_one({
                        "user_mail": ret['email'],
                        "user_id": str(ret['_id']),
                        "sending_time": datetime.datetime.now(),
                        "message": message_str,
                        "mail_sended_status": working_status,
                        "subject":subject,
                        "recipients": to

                    })


                campaign = mongo.db.campaigns.update({"_id":ObjectId(ret['campaign'])},
                    {
                        "$set": {
                                "cron_status": True
                            }
                            })

                user_status = mongo.db.campaign_users.update({"_id":ObjectId(ret['_id'])},
                    {
                        "$set": {
                                "send_status": True
                            }
                            })
            else:
                pass
        else:
            pass
    else:
        pass
    


def reject_mail():
    ret = mongo.db.rejection_handling.find_one({"send_status":False})
    if ret is not None:
        mail = ret['email']
        message = ret['message']
        time = ret['rejection_time']  
        time_update = dateutil.parser.parse(time).strftime("%Y-%m-%dT%H:%M:%SZ")
        rejected_time = datetime.datetime.strptime(time_update,'%Y-%m-%dT%H:%M:%SZ')
        diffrence = datetime.datetime.utcnow() - rejected_time
        if diffrence.days >= 1:
            to = []
            to.append(mail)
            send_email(message=message,recipients=to,subject='REJECTED')
            user_status = mongo.db.rejection_handling.remove({"_id":ObjectId(ret['_id'])})
        else:
            pass
    else:
        pass

def cron_messages():
    ret = mongo.db.messages_cron.find_one({"cron_status":False})
    if ret is not None:
        vet = mongo.db.messages_cron.update({"_id":ObjectId(ret['_id'])},
            {
                "$set": {
                        "cron_status": True
                    }
                    })

        if ret['type'] == "email":
            send_email(message=ret['message'],recipients=ret['recipients'],subject=ret['subject'])
        elif ret['type'] == "slack":
            slack_message(message=ret['message'],channel=ret['channel'],req_json=ret['req_json'],message_detail=ret['message_detail'])
        else:
            pass    
    else:
        pass 
        

def bounced_mail():
    print("bounced mail running")
    imapObj = imapclient.IMAPClient('imap.gmail.com', ssl=True)
    imapObj.login('rasealex000000@gmail.com','Rase@123')
    imapObj.select_folder('INBOX')

    search_bounce_mails=imapObj.search(['FROM','mailer-daemon@googlemail.com'])

    #all_bounced_mails = []
    for search_bounce_mail in search_bounce_mails:
        rawMessages = imapObj.fetch(search_bounce_mail,['BODY[]'])
        message_body = pyzmail.PyzMessage.factory(rawMessages[search_bounce_mail][b'BODY[]'])
        mail_subject = message_body.get_subject()
        mail_from =message_body.get_addresses('from')
        mail_to =message_body.get_addresses('to')
        if message_body.text_part != None:
            mail_text = message_body.text_part.get_payload().decode(message_body.text_part.charset)
            text_lists = mail_text.split()
            count = 0
            for text_list in text_lists:
                if text_list == 'delivered':
                    mail_checker = count+1
                    if text_lists[mail_checker] == 'to':
                        email_index = mail_checker + 1
                        bounced_mail = text_lists[email_index]
                        ret = mongo.db.bounce_emails.update({
                                "bounced_mail": bounced_mail
                            }, {
                                "$set": {
                                    "bounced_mail": bounced_mail
                                }},upsert=True)
                count = count + 1

