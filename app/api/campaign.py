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
from werkzeug import secure_filename


bp = Blueprint('campaigns', __name__, url_prefix='/')

@bp.route('/create_campaign', methods=["GET", "POST"])
# @token.admin_required
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
        ret = mongo.db.campaigns.insert_one({
                "Campaign_name": name,
                "creation_date": datetime.datetime.utcnow(),
                "Campaign_description": description,
                "message": message,
                "message_subject": message_subject,
                "status":status,
                "generated_from_recruit":generated
        }).inserted_id
        return jsonify(str(ret)),200

@bp.route('/attached_file/<string:Id>', methods=["POST","DELETE"])
def attache_campaign(Id):
    if request.method == "POST":
        file = request.files['attachment_file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))    
            attachment_file = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            attachment_file_name = filename     
            ret = mongo.db.campaigns.update({"_id":ObjectId(Id)},{
                "$set":{
                    "attachment_file_name": attachment_file_name,
                    "attachment_file": attachment_file
                }
            })
            return jsonify({"message": "File attached to campaign"}), 200
        else:
            return jsonify({"message": "Please select a file"}), 400
    elif request.method == "DELETE":
        ret = mongo.db.campaigns.find_one({
            "_id":ObjectId(Id),
            "attachment_file_name":{ "$exists": True},
            "attachment_file":{ "$exists": True}
        })
        if ret is not None:
            ret = mongo.db.campaigns.update({"_id":ObjectId(Id)},{
                "$unset":{
                    "attachment_file_name": 1,
                    "attachment_file": 1
                }
            })
            return jsonify({"message": "File deleted from campaign"}), 200
        else:
            return jsonify({"message": "File not attached to campaign"}), 200


@bp.route('/pause_campaign/<string:Id>/<int:status>', methods=["POST"])
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
def delete_campaign(Id):
    ret = mongo.db.campaigns.remove({"_id":ObjectId(Id)})
    return jsonify({"message":"Campaign deleted"}),200

@bp.route('/list_campaign', methods=["GET"])
# @token.admin_required
def list_campaign():
        ret = mongo.db.campaigns.aggregate([{"$sort" : { "creation_date" : -1}}])
        ret = [Template_details(serialize_doc(doc)) for doc in ret]
        return jsonify(ret), 200

@bp.route('/update_campaign/<string:Id>', methods=["PUT"])
# @token.admin_required
def update_campaign(Id):
    name = request.json.get("campaign_name")
    description = request.json.get("campaign_description")
    status = request.json.get("status")  
    message = request.json.get("message",None)
    message_subject = request.json.get("message_subject",None) 
    ret = mongo.db.campaigns.update({"_id": ObjectId(Id)},{
    "$set": {
        "Campaign_name": name,
        "Campaign_description": description,
        "status": status,
        "message": message,
        "message_subject": message_subject
    }
    })
    return jsonify({"message":"Campaign Updated"}),200

@bp.route('/assign_template/<string:campaign_id>/<string:template_id>', methods=["DELETE"])
@bp.route('/assign_template/<string:campaign_id>', methods=["PUT"])
def assign_template(campaign_id,template_id=None):
    if request.method == "PUT":
        for template_id in request.json['templates']:
            vac = mongo.db.campaigns.aggregate([
                { "$match": { "_id": ObjectId(campaign_id)}},
                { "$project": {"status":{"$cond":{"if":{"$ifNull": ["$Template",False]},"then":{"state": {"$in":[template_id,"$Template"]}},"else":{"state":False }}}}},
            ])
            for data in vac:
                if data['status'] is not None and data['status']['state'] is False:
                    ret = mongo.db.campaigns.update({"_id":ObjectId(campaign_id)},{
                        "$push": {
                            "Template": template_id  
                        }
                    })
        return jsonify({"message":"Template added to campaign"}), 200
    if request.method == "DELETE":
        vac = mongo.db.campaigns.aggregate([
            { "$match": { "_id": ObjectId(campaign_id)}},
            { "$project": {"status": {"$in":[template_id,"$Template"]},"count": { "$cond": { "if": { "$isArray": "$Template" }, "then": { "$size": "$Template" }, "else": "NULL"} }}},
        ])
        vac = [serialize_doc(doc) for doc in vac]
        for data in vac:
            if data['status'] is True:
                ret = mongo.db.campaigns.update({"_id":ObjectId(campaign_id)},{
                    "$pull": {
                        "Template": template_id  
                    }
                })
                return jsonify({"message":"Template removed from campaign"}), 200
            else:
                return jsonify({"message":"Template does not exist in this campaign"}), 400


@bp.route('/user_list_campaign',methods=["GET","POST"])
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
          
@bp.route("/campaign_detail/<string:Id>", methods=["GET"])
def campaign_detail(Id):
    ret = mongo.db.campaigns.find_one({"_id": ObjectId(Id)})
    detail = serialize_doc(ret)
    return jsonify(user_data(detail)),200

@bp.route("/campaign_smtp_test", methods=["POST"])
def campaign_smtp_test():
    mail = mongo.db.mail_settings.find({"origin":"CAMPAIGN"})
    mail = [serialize_doc(doc) for doc in mail]
    not_working = []
    for data in mail:
        try:
            send_email(
                message='SMTP TEST SUCCESFUL',
                recipients=[request.json.get('email')],
                subject='SMTP TEST',
                sending_mail= data['mail_username'],
                sending_password=data['mail_password'],
                sending_server=data['mail_server'],
                sending_port=data['mail_port']
                )
            sending_for.append(data['mail_server'])
            mongo.db.mail_settings.update({"_id":ObjectId(data)},{
                "$set":{
                "current_working_status" : True
            }})
        except Exception:
            not_working.append({"server":data['mail_server'],"reason": "something went wrong"})
        except smtplib.SMTPDataError:
            not_working.append({"server":data['mail_server'],"reason": "account not activated"})
        except smtplib.SMTPAuthenticationError:
            not_working.append({"server":data['mail_server'],"reason": "username and password is wrong"})

    return jsonify({"message": "sended"}),200

@bp.route("/campaign_mails/<string:campaign>", methods=["POST"])
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
                campaign_status = mongo.db.campaigns.update({"_id": ObjectId(campaign)},{
                    "$set": {
                        "status": "Running",
                        "delay": delay,
                        "smtps": smtps
                    }
                })
                return jsonify({"message":"Mails sended"}),200
    else:
        return jsonify({"message":"Please select smtps"}),400

@bp.route("/mails_status",methods=["GET"])
def mails_status():
    limit = request.args.get('limit',default=0, type=int)
    skip = request.args.get('skip',default=0, type=int)         
    ret = mongo.db.mail_status.find({}).skip(skip).limit(limit)
    ret = [serialize_doc(doc) for doc in ret]        
    return jsonify(ret), 200

@bp.route("/template_hit_rate/<string:variable>/<string:user>",methods=['GET'])
def hit_rate(variable,user):
    hit = request.args.get('hit_rate', default=0, type=int)
    hit_rate_calculation = mongo.db.mail_status.update({
        "user_id":user,
        "digit": variable
        },
        {
            "$inc": {
                "hit_rate":hit
                },
            "$set":{
                "seen_date": datetime.datetime.utcnow(),
                "seen": True
            }
        })   
    return send_from_directory(app.config['UPLOAD_FOLDER'],'1pxl.jpg')

@bp.route("campaign_redirect/<string:unique_key>",methods=['GET'])
def redirectes(unique_key):
    url =  request.args.get('url', type=str)
    action = request.args.get('action', type=str,default='')
    clicked = mongo.db.mail_status.update({"digit": unique_key},{
        "$set":{
            "clicked": True
        }
    })
    final_link = url+action
    return redirect(final_link), 302

@bp.route('edit_templates/<string:template_id>',methods=["POST"])
def edit_template(template_id):
    mongo.db.mail_template.update({"_id": ObjectId(template_id)}, {
    "$set": request.json
    })
    return jsonify({
        "message": "Template Updated",
        "status": True}), 200