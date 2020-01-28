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
        mail = mongo.db.mail_settings.remove({"origin":origin,"_id": ObjectId(str(id))})
        return jsonify ({"message": "Smtp conf deleted"}), 200
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
        return jsonify ({"message": "Smtp conf set as active"}), 200


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
        email = app.config['to']
        if origin == "HR": 
            print("HR")
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
            except Exception as e:

                mongo.db.error_repr.insert_one({"issue": str(repr(e))})
                print(repr(e),"EXCEPTION")
                
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
                mongo.db.error_repr.insert_one({"issue": str(repr(e))})


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
                
