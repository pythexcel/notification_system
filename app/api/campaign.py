from app import mongo
from app import token
from flask import (Blueprint, flash, jsonify, abort, request, send_from_directory)
from app.util import serialize_doc,Template_details,campaign_details,user_data
import datetime
import dateutil.parser
from flask import current_app as app
from bson.objectid import ObjectId
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity, get_current_user, jwt_refresh_token_required,
    verify_jwt_in_request
)

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
        active = request.json.get("active",True)
        if not name:
            return jsonify({"message": "Invalid Request"}), 400    
        ret = mongo.db.campaigns.insert_one({
                "Campaign_name": name,
                "Campaign_description": description,
                "active":active,
                "cron_status": False
        }).inserted_id
        return jsonify(str(ret)),200
        
@bp.route('/delete_campaign/<string:Id>', methods=["DELETE"])
def delete_campaign(Id):
    ret = mongo.db.campaigns.remove({"_id":ObjectId(Id)})
    return jsonify({"message":"Campaign deleted"}),200

@bp.route('/list_campaign', methods=["GET"])
# @token.admin_required
def list_campaign():
        ret = mongo.db.campaigns.aggregate([])
        ret = [Template_details(serialize_doc(doc)) for doc in ret]
        return jsonify(ret), 200


@bp.route('/update_campaign/<string:Id>', methods=["PUT"])
# @token.admin_required
def update_campaign(Id):
    name = request.json.get("campaign_name")
    description = request.json.get("campaign_description")
    active = request.json.get("active")  
    ret = mongo.db.campaigns.update({"_id": ObjectId(Id)},{
    "$set": {
        "Campaign_name": name,
        "Campaign_description": description,
        "active":active
    }
    })
    return jsonify({"message":"Campaign Updated"}),200

@bp.route('/assign_template/<string:campaign_id>/<string:template_id>', methods=["PUT","DELETE"])
def assign_template(campaign_id,template_id):
    if request.method == "PUT":
        vac = mongo.db.campaigns.aggregate([
            { "$match": { "_id": ObjectId(campaign_id)}},
            { "$project": {"status":{"$cond":{"if":{"$ifNull": ["$Template",False]},"then":{"state": {"$in":[template_id,"$Template"]}},"else":{"state":False }}}}},
        ])
        for data in vac:
            print(data['status'])
            if data['status'] is not None and data['status']['state'] is False:
                ret = mongo.db.campaigns.update({"_id":ObjectId(campaign_id)},{
                    "$push": {
                        "Template": template_id  
                    }
                })
                return jsonify({"message":"Template added to campaign"}), 200
            else:
                return jsonify({"message":"Template exist in campaign"}), 200
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

        ret = mongo.db.campaign_users.insert_many(users)
        return jsonify({"message":"Users added to campaign"}), 200  


@bp.route("/campaign_detail/<string:Id>", methods=["GET"])
def campaign_detail(Id):
    ret = mongo.db.campaigns.find_one({"_id": ObjectId(Id)})
    detail = serialize_doc(ret)
    return jsonify(user_data(detail)),200

@bp.route("/campaign_mails", methods=["POST"])
def campaign_start_mail():
    ids = request.json.get("ids",[])
    final_ids = []
    for data in ids:
        final_ids.append(ObjectId(data))

    ret = mongo.db.campaign_users.update({"_id":{ "$in": final_ids}},{
        "$set":{
            "mail_cron":False
        }
    },multi=True)
    return jsonify({"Message":"Mails sended"}),200


@bp.route("/mails_status",methods=["GET"])
def mails_status():
    limit = request.args.get('limit',default=0, type=int)
    skip = request.args.get('skip',default=0, type=int)         
    ret = mongo.db.mail_status.find({}).skip(skip).limit(limit)
    ret = [serialize_doc(doc) for doc in ret]        
    return jsonify(ret), 200

@bp.route("/template_hit_rate/<string:variable>/<string:user>",methods=['GET'])
def hit_rate(variable,user):
    template =  request.args.get('template', type=str)
    hit = request.args.get('hit_rate', default=0, type=int)
    hit_rate_calculation = mongo.db.template_hitrate.update({
        "template":template,
        "user":user
        },
        {
            "$inc": {
                "hit_rate":hit
                },
            "$set":{
                "seen_date": datetime.datetime.now()
            }
        },upsert=True)   
    return send_from_directory(app.config['UPLOAD_FOLDER'],'1pxl.jpg')