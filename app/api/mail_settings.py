from app import mongo
from app import token
from flask import (Blueprint, flash, jsonify, abort, request)
from app.util import serialize_doc
import json
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity, get_current_user, jwt_refresh_token_required,
    verify_jwt_in_request
)
from flask import current_app as app
from bson import ObjectId
from app.mail_util import send_email,validate_smtp
import smtplib
import datetime


bp = Blueprint('mail_settings', __name__, url_prefix='/smtp')

@bp.route('/settings/<string:origin>', methods=["POST", "GET"])
@bp.route('/settings/<string:origin>/<string:id>', methods=["DELETE","PUT"])
#@token.admin_required
def mail_setings(origin,id=None):
    if request.method == "GET":
       mail = mongo.db.mail_settings.find({"origin":origin},{"mail_password":0})
       mail = [serialize_doc(doc) for doc in mail]
       return jsonify (mail)
    if request.method == "DELETE":
        prior = mongo.db.mail_settings.find_one({"origin":origin,"_id": ObjectId(str(id))})
        if origin == "CAMPAIGN":
            priority = prior['priority']
        else:
            pass     
        mail = mongo.db.mail_settings.remove({"origin":origin,"_id": ObjectId(str(id))})
        if origin == "CAMPAIGN":
            campaign_smtp = mongo.db.mail_settings.update({"origin":origin,"priority":{ "$gt": priority } },{
                        "$inc" :{
                            "priority": -1
                        }

                    },multi=True)
        return jsonify ({"message": "Smtp conf deleted"}), 200
    if request.method == "PUT":
        active = request.json.get("active", None)
        mail = mongo.db.mail_settings.update({"origin":origin,"_id": ObjectId(str(id))},{
            "$set":{
                "active" : active
            }
        })
        return jsonify ({"message": "Smtp conf status changed"}), 200


    if request.method == "POST":
        if not request.json:
            abort(500)
        mail_server = request.json.get("mail_server", "smtp.gmail.com")
        mail_port = request.json.get("mail_port", 465)
        mail_use_tls = request.json.get("mail_use_tls", True)
        mail_username = request.json.get("mail_username", None)
        mail_password = request.json.get("mail_password", None)
        mail_from  = request.json.get("mail_from", None)
        active = request.json.get("active",True)
        type_s = request.json.get("type", "tls")
        
        if not mail_server and mail_password and mail_port and mail_use_tls and mail_username:
            return jsonify({"message": "Invalid Request"}), 400  
        email = None
        if mail_from is not None:
            email = mail_from
        else:
            email = mail_username  
        try:
            send_email(message="SMTP WORKING!",recipients=[email],mail_from = mail_from,subject="SMTP TESTING MAIL!",sending_mail=mail_username,sending_password=mail_password,sending_port=mail_port,sending_server=mail_server)
        except smtplib.SMTPServerDisconnected:
            return jsonify({"message": "Smtp server is disconnected"}), 400                
        except smtplib.SMTPConnectError:
            return jsonify({"message": "Smtp is unable to established"}), 400    
        except smtplib.SMTPAuthenticationError:
            return jsonify({"message": "Smtp login and password is wrong"}), 400                           
        except smtplib.SMTPDataError:
            return jsonify({"message": "Smtp account is not activated"}), 400 
        except Exception:
            return jsonify({"message": "Something went wrong with smtp"}), 400
        else:   
            if origin == "HR": 
                    ret = mongo.db.mail_settings.update({}, {
                        "$set": {
                            "mail_server": mail_server,
                            "mail_port": mail_port,
                            "origin": origin,
                            "mail_use_tls": mail_use_tls,
                            "mail_username":mail_username,
                            "mail_password":mail_password,
                            "active": active,
                            "type": type_s,
                            "mail_from": mail_from
                        }
                    },upsert=True)
                    return jsonify({"message":"upsert"}),200

            elif origin == "RECRUIT":
                vet = mongo.db.mail_settings.find_one({"mail_username":mail_username,
                        "mail_password":mail_password,"origin":origin})
                if vet is None:
                    exist = mongo.db.mail_settings.find_one({"origin":origin,"active":True})
                    if exist is None:
                        active = True
                    else:
                        active = False    
                    ret = mongo.db.mail_settings.insert_one({
                        "mail_server": mail_server,
                            "mail_port": mail_port,
                            "origin": origin,
                            "mail_use_tls": mail_use_tls,
                            "mail_username":mail_username,
                            "mail_password":mail_password,
                            "active": active,
                            "type": type_s,
                            "mail_from": mail_from
                    }).inserted_id
                    return jsonify({"message":"upsert","id":str(ret)}),200
                else:
                    return jsonify({"message":"Smtp already exists"}),400

            elif origin == "CAMPAIGN":
                daemon_mail = None
                if mail_server == "smtp.gmail.com":
                    daemon_mail = "mailer-daemon@googlemail.com"
                elif mail_server == "smtp.mail.yahoo.com":
                    daemon_mail = "mailer-daemon@yahoo.com"
                elif mail_server == "smtp.office365.com":
                    daemon_mail = "postmaster@outlook.com"
                vet = mongo.db.mail_settings.find_one({"mail_username":mail_username,
                        "mail_password":mail_password,"origin":origin})
                if vet is None:
                    priority = 1
                    previous =  mongo.db.mail_settings.find({"origin":"CAMPAIGN"}).sort("priority", -1).limit(1)
                    prior_check = [serialize_doc(doc) for doc in previous]
                    if prior_check:
                        for data in prior_check:
                            priority = data['priority'] + 1
                    ret = mongo.db.mail_settings.insert_one({
                            "mail_server": mail_server,
                            "mail_port": mail_port,
                            "origin": origin,
                            "mail_use_tls": mail_use_tls,
                            "mail_username":mail_username,
                            "mail_password":mail_password,
                            "active": active,
                            "type": type_s,
                            "daemon_mail":daemon_mail,
                            "priority": priority,
                            "mail_from": mail_from,
                            "created_at": datetime.datetime.today()

                    }).inserted_id
                    return jsonify({"message":"upsert","id":str(ret)}),200
                else:
                    return jsonify({"message":"Smtp already exists"}),400

@bp.route('/smtp_priority/<string:Id>/<int:position>', methods=["POST"])
#@token.admin_required
def smtp_priority(Id,position):
    prior_check = mongo.db.mail_settings.find({"origin": "CAMPAIGN"}).sort("priority",1)
    prior_check = [serialize_doc(doc) for doc in prior_check]
    index = 0
    value = 0
    for data in prior_check:
        if str(data['_id']) == str(Id):
            value = index
        index = index + 1
    val = None
    if position == 1:
        val = value - 1
    elif position == 0:
        val = value + 1    
    final = prior_check[val]
    current = prior_check[value]
    ret = mongo.db.mail_settings.update({"_id":ObjectId(Id)},{
        "$set":{
            "priority": final['priority']
        }
    },upsert=False)
    vet = mongo.db.mail_settings.update({"_id":ObjectId(final['_id'])},{
        "$set":{
            "priority": current['priority']
        }
    },upsert=False) 

    return jsonify({"message": "priority changed"}), 200

@bp.route('/update_settings/<string:origin>/<string:id>', methods=["PUT"])
#@token.admin_required
def update_smtp(origin,id):
    new_password = request.json.get('new_password',"password")
    mail_details = mongo.db.mail_settings.find_one({"_id": ObjectId(str(id))})
    if mail_details is None:
        return jsonify({"message": "No smtp exists"}),400
    else:
        username = mail_details["mail_username"]
        password = mail_details["mail_password"]
        port = mail_details['mail_port']
        mail_server = mail_details['mail_server']
        mail_from = mail_details['mail_from']

        email = None
        if mail_from is not None:
            email = mail_from
        else:
            email = username 
        try:
            send_email(message="SMTP WORKING!",recipients=[email],mail_from = mail_from,subject="SMTP TESTING MAIL!",sending_mail=username,sending_password=new_password,sending_port=port,sending_server=mail_server)
        except smtplib.SMTPServerDisconnected:
            return jsonify({"message": "Smtp server is disconnected"}), 400                
        except smtplib.SMTPConnectError:
            return jsonify({"message": "Smtp is unable to established"}), 400    
        except smtplib.SMTPAuthenticationError:
            return jsonify({"message": "Smtp login and password is wrong"}), 400                           
        except smtplib.SMTPDataError:
            return jsonify({"message": "Smtp account is not activated"}), 400 
        except Exception:
            return jsonify({"message": "Something went wrong with smtp"}), 400
        else:
            mail = mongo.db.mail_settings.update({"origin":origin,"_id": ObjectId(str(id))},{
                "$set":{
                    "mail_password": new_password
                }
            })
            return jsonify({"message": "Smtp password updated"}), 200

@bp.route('/validate_smtp', methods=["POST"])
#@token.admin_required
def validate_smtp():
    email = request.json.get('email')
    password = request.json.get('password')
    if email is None:
        return jsonify({"message": "please enter a email"}), 400
    try:
        validate_smtp(username=email,password=password,port=465,smtp="smtp.gmail.com")
    except Exception:
            return jsonify({"message": "smtp login and password failed"}), 400
    else:
        return jsonify({"message": "login succesfull"}), 200
