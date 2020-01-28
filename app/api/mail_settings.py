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
from app.mail_util import send_email
import smtplib
import datetime


bp = Blueprint('mail_settings', __name__, url_prefix='/smtp')

@bp.route('/settings/<string:origin>', methods=["POST", "GET"])
@bp.route('/settings/<string:origin>/<string:id>', methods=["DELETE","PUT"])
# @token.admin_required
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
            campaign_smtp = mongo.db.mail_settings.update({"priority":{ "$gt": priority } },{
                        "$inc" :{
                            "priority": -1
                        }

                    },multi=True)
        return jsonify ({"Message": "Smtp conf deleted"}), 200
    if request.method == "PUT":
        ret = mongo.db.mail_settings.update({"origin":origin,"active":True},{
            "$set":{
                "active" : False
            }

        },multi=True)
        mail = mongo.db.mail_settings.update({"origin":origin,"_id": ObjectId(str(id))},{
            "$set":{
                "active" : True
            }

        })
        return jsonify ({"Message": "Smtp conf set as active"}), 200


    if request.method == "POST":
        if not request.json:
            abort(500)
            #checking origin of api hit so if it is HR one smtp conf can be created or updated only
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
            if origin == "HR": 
                try:
                    send_email(message="SMTP WORKING!",recipients=[email],subject="SMTP TESTING MAIL!",sending_mail=mail_username,sending_password=mail_password,sending_port=mail_port,sending_server=mail_server)
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
                    ret = mongo.db.mail_settings.update({}, {
                        "$set": {
                            "mail_server": mail_server,
                            "mail_port": mail_port,
                            "origin": origin,
                            "mail_use_tls": mail_use_tls,
                            "mail_username":mail_username,
                            "mail_password":mail_password,
                            "mail_from": mail_from
                        }
                    },upsert=True)
                    return jsonify({"message":"upsert"}),200

            elif origin == "RECRUIT":
                email = app.config['to']
                smtp_right = True
                unregister = False
                try:
                    send_email(message="SMTP WORKING!",recipients=[email],subject="SMTP TESTING MAIL!",sending_mail=mail_username,sending_password=mail_password,sending_port=mail_port,sending_server=mail_server)
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
                    vet = mongo.db.mail_settings.find_one({"mail_username":mail_username,
                            "mail_password":mail_password,"origin":origin})
                    if vet is None:
                        exist = mongo.db.mail_settings.find_one({"origin":origin})
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
                        })
                        return jsonify({"message":"upsert"}),200
                    else:
                        return jsonify({"message":"Smtp already exists"}),400

        elif origin == "CAMPAIGN":  
            email = app.config['to']
            smtp_right = True
            unregister = False
            credentails = True
            try:
                send_email(message="SMTP WORKING!",recipients=[email],subject="SMTP TESTING MAIL!",sending_mail=mail_username,sending_password=mail_password,sending_port=mail_port,sending_server=mail_server)
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
                            "priority": priority,
                            "created_at": datetime.datetime.today()


                    })
                    return jsonify({"message":"upsert"}),200
                else:
                    return jsonify({"message":"Smtp already exists"}),400

@bp.route('/smtp_priority/<string:Id>/<int:position>', methods=["POST"])
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
