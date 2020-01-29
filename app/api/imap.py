from app import mongo
from flask import (Blueprint, flash, jsonify, abort, request)
from app.util import serialize_doc
import json
import imapclient
import pyzmail
import email
import datetime
import pprint
import re
from dateutil.parser import parse



bp = Blueprint('imap', __name__, url_prefix='/imap')



@bp.route('/get_emails',methods=["POST"])
def get_emails():
    if request.method == "POST":
        imap_server = request.json.get("imap_server",None)
        mail_username = request.json.get("mail_username",None)
        smtp_values = mongo.db.mail_settings.find_one({"mail_username":mail_username,"active":True})
        if smtp_values is not None:
            mail_password = smtp_values['mail_password']
            if imap_server and mail_username is not None:
                try:
                    print("trying login")
                    imapObj = imapclient.IMAPClient(imap_server, ssl=True)
                    imapObj.login(mail_username,mail_password)
                except Exception as e:
                    return jsonify({"error":e}),400
                else:
                    print("login successfully")
                    imapObj.select_folder('INBOX')
                    date = datetime.datetime.now()-datetime.timedelta(days=7)
                    mail_frm=date.strftime("%d-%b-%Y")
                    recieved_mails=imapObj.search(['SINCE',mail_frm])
                    search_bounce_mails =  recieved_mails 
                    emails = []
                    if search_bounce_mails:
                        for search_bounce_mail in search_bounce_mails:
                            rawMessages = imapObj.fetch(search_bounce_mail,['BODY[]'])
                            message_body = pyzmail.PyzMessage.factory(rawMessages[search_bounce_mail][b'BODY[]'])
                            mail_subject = message_body.get_subject()
                            mail_from =message_body.get_address('from')[1]
                            mail_to =message_body.get_address('to')[1]
                            date =message_body.get_decoded_header('date')
                            print(mail_from)
                            if {"mail_from":mail_from} not in emails:
                                emails.append({"mail_from":mail_from})
                        print(emails)
                        return jsonify(emails),200
                    else:
                        return jsonify({"error":"No mails available from this date"}),400
            else:
                return jsonify({"error":"Payload are not valid somthing missing"}),400
        else:
            return jsonify({"error":"This username is not Available"}),400
    else:
        return jsonify({"error":"Method not allowed"}),400
    


@bp.route('/get_chat',methods=["POST"])
def get_chats():
    if request.method == "POST":
        imap_server = request.json.get("imap_server",None)
        mail_username = request.json.get("mail_username",None)
        chat_email = request.json.get("chat_email",None)
        smtp_values = mongo.db.mail_settings.find_one({"mail_username":mail_username,"active":True})
        if smtp_values is not None:
            mail_password = smtp_values['mail_password']
            if imap_server and mail_username and chat_email is not None:
                try:
                    print("trying login")
                    imapObj = imapclient.IMAPClient(imap_server, ssl=True)
                    imapObj.login(mail_username,mail_password)
                except Exception as e:
                    return jsonify({"error":e}),400
                else:
                    print("login successfully")
                    imapObj.select_folder('INBOX')
                    sended_ma=imapObj.search(['FROM',mail_username,'TO',chat_email])
                    recieved_mails = imapObj.search(['FROM',chat_email,'TO',mail_username])
                    sended_mails = sended_ma + recieved_mails
                    emails = []
                    if sended_mails:
                        for sended_mail in sended_mails:
                            rawMessages = imapObj.fetch(sended_mail,['BODY[]'])
                            message_body = pyzmail.PyzMessage.factory(rawMessages[sended_mail][b'BODY[]'])
                            mail_subject = message_body.get_subject()
                            mail_from =message_body.get_address('from')[1]
                            mail_to =message_body.get_address('to')[1]
                            date =message_body.get_decoded_header('date')
                            dt = parse(date)
                            mail_time=dt.strftime("%b %d %Y %H:%M:%S")
                            if message_body.text_part.charset != None: #checking if msg body have text part
                                mail_text = message_body.text_part.get_payload().decode(message_body.text_part.charset)
                                d = mail_text.split("wrote:")[0]
                            emails.append({"mail_subject":mail_subject,"mail_from":mail_from,"mail_to":mail_to,"datetime":mail_time,"message":d})
                        sortedArray = sorted(emails,key=lambda x: datetime.datetime.strptime(x['datetime'],"%b %d %Y %H:%M:%S"), reverse=True)
                        return jsonify(sortedArray),200
                    else:
                        return jsonify(emails),200
            else:
                return jsonify({"error":"Payload are not valid somthing missing"}),400
        else:
            return jsonify({"error":"Username is not available in DB"}),400
    else:
        return jsonify({"error":"Method not allowed"}),400




