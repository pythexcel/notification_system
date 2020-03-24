import os
from app import mongo
from app import token
from flask import (Blueprint, flash, jsonify, abort, request, send_from_directory,redirect)
from app.util import serialize_doc,Template_details,campaign_details,user_data,allowed_file
import datetime
import pymongo.errors
import dateutil.parser
from flask import current_app as app
from bson.objectid import ObjectId
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity, get_current_user, jwt_refresh_token_required,
    verify_jwt_in_request
)
from app.mail_util import send_email,validate_smtp_counts,validate_smtp
import smtplib
from app.config import smtp_counts
from werkzeug import secure_filename
import uuid


bp = Blueprint('campaigns', __name__, url_prefix='/')

@bp.route('/create_campaign', methods=["GET", "POST"])
#@token.admin_required
def create_campaign():
    if request.method == "GET":
        ret = mongo.db.campaigns.aggregate([])
        ret = [Template_details(serialize_doc(doc)) for doc in ret]
        return jsonify(ret)
    if request.method == "POST":
        name = request.json.get("campaign_name",None)
        description = request.json.get("campaign_description",None)
        status = request.json.get("status","Idle")
        message = request.json.get("message",None)
        message_subject = request.json.get("message_subject",None) 
        generated = request.json.get("generated_from_recruit",False)
        if not name:
            return jsonify({"message": "Invalid Request"}), 400   

        message_creation = dict()
        if message is not None and message_subject is not None:
            message_id = str(uuid.uuid4())
            message_creation.update({"message_id": message_id, "message": message,"message_subject": message_subject,"count":0})

        ret = mongo.db.campaigns.insert_one({
                "Campaign_name": name,
                "creation_date": datetime.datetime.utcnow(),
                "Campaign_description": description,
                "status":status,
                "generated_from_recruit":generated
        }).inserted_id

        if message_creation is not None:
            create_campaign_message = mongo.db.campaigns.update({"_id": ObjectId(str(ret))},{
                "$push": {
                   "message_detail" : message_creation
                }
            })
        else:
            pass
    
        return jsonify({"campaign_id":str(ret),"message_id":message_id}),200

@bp.route('/attached_file/<string:Id>/<string:message_id>', methods=["POST","DELETE"])
#@token.admin_required
def attache_campaign(Id,message_id):
    if request.method == "POST":
        file = request.files['attachment_file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))    
            attachment_file = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            attachment_file_name = filename   
            ret = mongo.db.campaigns.update({"_id":ObjectId(Id),"message_detail.message_id":message_id},{
                "$set":{
                    "message_detail.$.attachment_file_name": attachment_file_name,
                    "message_detail.$.attachment_file": attachment_file
                }
            })
            return jsonify({"message": "File attached to campaign"}), 200
        else:
            return jsonify({"message": "Please select a file"}), 400
    elif request.method == "DELETE":
        ret = mongo.db.campaigns.update({"_id":ObjectId(Id),"message_detail.message_id":message_id},{
            "$unset":{
                "message_detail.$.attachment_file_name": 1,
                "message_detail.$.attachment_file": 1
            }
        })
        return jsonify({"message": "File deleted from campaign"}), 200



@bp.route('/pause_campaign/<string:Id>/<int:status>', methods=["POST"])
#@token.admin_required
def pause_campaign(Id,status):
    working = None
    if status == 1:
        block = False
        working = "Running"
    elif status == 0:
        block = True
        working = "Paused"

    ret = mongo.db.campaigns.update({"_id":ObjectId(Id)},{
        "$set": {
            "status": working
        }
    })
    users = mongo.db.campaign_users.update({"campaign":Id},{
        "$set": {
            "block": block
        }
    },multi=True)
    return jsonify({"message":"Campaign status changed to {}".format(working)}),200


@bp.route('/delete_campaign/<string:Id>', methods=["DELETE"])
#@token.admin_required
def delete_campaign(Id):
    ret = mongo.db.campaigns.remove({"_id":ObjectId(Id)})
    return jsonify({"message":"Campaign deleted"}),200

@bp.route('/list_campaign', methods=["GET"])
#@token.admin_required
def list_campaign():
        ret = mongo.db.campaigns.aggregate([{"$sort" : { "creation_date" : -1}}])
        ret = [Template_details(serialize_doc(doc)) for doc in ret]
        return jsonify(ret), 200

@bp.route('/update_campaign/<string:Id>', methods=["POST"])
@bp.route('/update_campaign/<string:Id>/<string:message_id>', methods=["DELETE"])
#@token.admin_required
def update_campaign(Id,message_id=None):
    if request.method == "POST":
        name = request.json.get("campaign_name")
        description = request.json.get("campaign_description")
        status = request.json.get("status")  
        message = request.json.get("message",None)
        message_subject = request.json.get("message_subject",None)
        message_id = request.json.get("message_id",None)
        message_detail = request.json.get("message_detail",[])
        if message_id is not None:
            campaign = mongo.db.campaigns.update({"_id": ObjectId(Id),"message_detail.message_id": message_id},{
            "$set": {
                "Campaign_name": name,
                "Campaign_description": description,
                "status": status,
                "message_detail.$.message": message,
                "message_detail.$.message_subject": message_subject
            }
            })
            return jsonify({"message":"Campaign Updated with message","message_id":message_id}),200
        else:
            if message_detail:
                message_ids = []
                for data in message_detail:
                    data['message_id'] = str(uuid.uuid4())
                    data['count'] = 0
                    message_ids.append(data['message_id'])
                    campaign = mongo.db.campaigns.update({"_id": ObjectId(Id)},{
                    "$set": {
                        "Campaign_name": name,
                        "Campaign_description": description,
                        "status": status
                    },
                    "$push": { 
                        "message_detail" : data
                        }
                    })
            else:
                campaign = mongo.db.campaigns.update({"_id": ObjectId(Id)},{
                "$set": {
                    "Campaign_name": name,
                    "Campaign_description": description,
                    "status": status
                }                
                })
            return jsonify({"message":"Campaign Updated","message_id":message_ids}),200
    elif request.method == "DELETE":
        campaign = mongo.db.campaigns.update({"_id": ObjectId(Id)},{
        "$pull": {
            "message_detail":{
                "message_id": message_id

            } 
        }
        })
        return jsonify({"message": "message deleted from campaign"})

@bp.route('/user_list_campaign',methods=["GET","POST"])
#@token.admin_required
def add_user_campaign():
    if request.method == "GET":
        ret = mongo.db.campaign_users.aggregate([])
        ret = [campaign_details(serialize_doc(doc)) for doc in ret]
        return jsonify(ret), 200
    if request.method == "POST":
        users = request.json.get("users")
        campaign = request.json.get("campaign")
        for data in users:
            data['send_status'] = False
            data['campaign'] = campaign
            data['block'] = False
        mongo.db.campaign_users.create_index( [ ("email" , 1  ),( "campaign", 1 )], unique = True)
        try:
            ret = mongo.db.campaign_users.insert_many(users)
            return jsonify({"message":"Users added to campaign"}), 200
        except pymongo.errors.BulkWriteError as bwe:
            return jsonify({"message":"Users added to campaign and duplicate users will not be added"}), 200

@bp.route('/user_delete_campaign/<string:campaign_id>/<string:user_id>',methods=["DELETE"])
def delete_user_campaign(campaign_id,user_id):
    ret = mongo.db.campaign_users.remove({"_id": ObjectId(user_id),"campaign":campaign_id})
    return jsonify({"message":"User deleted from campaign"}), 200
        
          
@bp.route("/campaign_detail/<string:Id>", methods=["GET"])
#@token.admin_required
def campaign_detail(Id):
    ret = mongo.db.campaigns.find_one({"_id": ObjectId(Id)})
    detail = serialize_doc(ret)
    return jsonify(user_data(detail)),200

@bp.route("/campaign_smtp_test", methods=["POST"])
#@token.admin_required
def campaign_smtp_test():
    mail = mongo.db.mail_settings.find({"origin":"CAMPAIGN"})
    mail = [serialize_doc(doc) for doc in mail]
    working = []
    for data in mail:
        try:
            send_email(
                message=request.json.get('message'),
                recipients=[request.json.get('email')],
                subject=request.json.get('message_subject'),
                sending_mail= data['mail_username'],
                sending_password=data['mail_password'],
                sending_server=data['mail_server'],
                sending_port=data['mail_port']
                )
        except smtplib.SMTPServerDisconnected:
            return jsonify({"smtp": data['mail_server'],"mail":data['mail_username'],"message": "Smtp server is disconnected"}), 400                
        except smtplib.SMTPConnectError:
            return jsonify({"smtp": data['mail_server'],"mail":data['mail_username'],"message": "Smtp is unable to established"}), 400    
        except smtplib.SMTPAuthenticationError:
            return jsonify({"smtp": data['mail_server'],"mail": data['mail_username'],"message": "Smtp login and password is wrong"}), 400                           
        except smtplib.SMTPDataError:
            return jsonify({"smtp": data['mail_server'],"mail":data['mail_username'],"message": "Smtp account is not activated"}), 400 
        except Exception:
            return jsonify({"smtp": data['mail_server'],"mail": data['mail_username'],"message": "Something went wrong with smtp"}), 400
        
    return jsonify({"message": "sended"}),200

@bp.route("/campaign_mails/<string:campaign>", methods=["POST"])
#@token.admin_required
def campaign_start_mail(campaign):   
    delay = request.json.get("delay",30)
    smtps = request.json.get("smtps",[])
    ids = request.json.get("ids",[])
    final_ids = []
    if smtps:
        for smtp in smtps:
            smtp_values = mongo.db.mail_settings.find_one({"_id":ObjectId(smtp)})
            try:
                validate = validate_smtp(username=smtp_values['mail_username'],password=smtp_values['mail_password'],port=smtp_values['mail_port'],smtp=smtp_values['mail_server'])
            
            except smtplib.SMTPServerDisconnected:
                return jsonify({"smtp": smtp_values['mail_server'],"mail":smtp_values['mail_username'],"message": "Smtp server is disconnected"}), 400                
            except smtplib.SMTPConnectError:
                return jsonify({"smtp": smtp_values['mail_server'],"mail":smtp_values['mail_username'],"message": "Smtp is unable to established"}), 400    
            except smtplib.SMTPAuthenticationError:
                return jsonify({"smtp": smtp_values['mail_server'],"mail":smtp_values['mail_username'],"message": "Smtp login and password is wrong"}), 400                           
            except smtplib.SMTPDataError:
                return jsonify({"smtp": smtp_values['mail_server'],"mail":smtp_values['mail_username'],"message": "Smtp account is not activated"}), 400 
            except Exception:
                return jsonify({"smtp": smtp_values['mail_server'],"mail":smtp_values['mail_username'],"message": "Something went wrong with smtp"}), 400
        
            else:
                for data in ids:
                    final_ids.append(ObjectId(data))
                ret = mongo.db.campaign_users.update({"_id":{ "$in": final_ids}},{
                    "$set":{
                        "mail_cron":False
                    }
                },multi=True)
                smtp_count_value = []
                for smtp in smtps:
                    smtp_detail = mongo.db.mail_settings.find_one({"_id": ObjectId(smtp)})
                    if smtp_detail['mail_server'] in smtp_counts:
                        for key,value in smtp_counts.items():
                            if key == smtp_detail['mail_server']:
                                smtp_count_value.append(value)

                total_time = (float(len(ids))* delay / float(len(smtp_count_value)))
                if total_time <= 60:
                    total_time = round(total_time,2)
                    total_expected_time = "{} second".format(total_time)
                elif total_time>60 and total_time<=3600:
                    total_time = total_time/60
                    total_time = round(total_time,1)
                    total_expected_time = "{} minutes".format(total_time)
                elif total_time>3600 and total_time<=86400:
                    total_time = total_time/3600
                    total_time = round(total_time,1)
                    total_expected_time = "{} hours".format(total_time)
                else:
                    total_time = total_time/86400
                    total_time = round(total_time,1)
                    total_expected_time = "{} days".format(total_time)
                campaign_status = mongo.db.campaigns.update({"_id": ObjectId(campaign)},{
                    "$set": {
                        "status": "Running",
                        "delay": delay,
                        "smtps": smtps,
                        "total_expected_time_of_completion": total_expected_time
                    }
                })
                return jsonify({"message":"Mails sended"}),200
    else:
        return jsonify({"message":"Please select smtps"}),400

@bp.route("/mails_status",methods=["GET"])
#@token.admin_required
def mails_status():
    limit = request.args.get('limit',default=0, type=int)
    skip = request.args.get('skip',default=0, type=int)         
    ret = mongo.db.mail_status.find({}).skip(skip).limit(limit)
    ret = [serialize_doc(doc) for doc in ret]        
    return jsonify(ret), 200

@bp.route("/template_hit_rate/<string:variable>/<string:campaign_message>/<string:user>",methods=['GET'])
def hit_rate(variable,campaign_message,user):
    hit = request.args.get('hit_rate', default=0, type=int)

    campaign_update = mongo.db.campaigns.update({"message_detail.message_id": campaign_message },{
        "$inc": 
        {
            "message_detail.$.count":hit
        },
    })
    hit_rate_calculation = mongo.db.mail_status.update({
        "user_id":user,
        "digit": variable
        },{
        "$set":{
            "seen_date": datetime.datetime.utcnow(),
            "seen": True
        }
        })   
    return send_from_directory(app.config['UPLOAD_FOLDER'],'1pxl.jpg')

@bp.route("campaign_redirect/<string:unique_key>/<string:campaign_id>",methods=['GET'])
def redirectes(unique_key,campaign_id):
    url =  request.args.get('url', type=str)
    clicked = mongo.db.mail_status.update({"digit": unique_key},{
        "$set":{
            "clicked": True
        }
    })
    campaign_clicked_details = mongo.db.campaign_clicked.insert_one({
        "campaign_id": campaign_id,
        "clicked_time": datetime.datetime.now()
    })
    return redirect(url), 302

@bp.route('edit_templates/<string:template_id>',methods=["POST"])
def edit_template(template_id):
    mongo.db.mail_template.update({"_id": ObjectId(template_id)}, {
    "$set": request.json
    })
    return jsonify({
        "message": "Template Updated",
        "status": True}), 200


@bp.route('/daily_validate_details',methods = ["GET"])
def validate_details():
    limit = request.args.get('limit',default=0, type=int)
    skip = request.args.get('skip',default=0, type=int)         
    ret = mongo.db.smtp_count_validate.find({}).skip(skip).limit(limit)
    ret = [serialize_doc(doc) for doc in ret]        
    return jsonify(ret), 200

@bp.route("/unsubscribe_mail/<string:unsubscribe_mail>",methods=['GET'])
def unsubscribe_mail(unsubscribe_mail):
    unsubscribe = mongo.db.unsubscribe_mails.update({
        "email":unsubscribe_mail,
        },{
        "$set":{
            "unsubscribe_at": datetime.datetime.utcnow(),
            "email": unsubscribe_mail
        }
        },upsert=True)
    return "unsubscribed successfully"


@bp.route("/unsubscribe_mails_list",methods=["GET"])
#@token.admin_required
def unsubscribe_mails_list():
    limit = request.args.get('limit',default=0, type=int)
    skip = request.args.get('skip',default=0, type=int)         
    ret = mongo.db.unsubscribe_mails.find({}).skip(skip).limit(limit)
    ret = [serialize_doc(doc) for doc in ret]        
    return jsonify(ret), 200