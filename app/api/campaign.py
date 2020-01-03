from app import mongo
from app import token
from flask import (Blueprint, flash, jsonify, abort, request)
from app.util import serialize_doc,Template_details,campaign_details
import datetime
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
            return jsonify({"msg": "Invalid Request"}), 400    
        ret = mongo.db.campaigns.insert_one({
                "Campaign_name": name,
                "Campaign_description": description,
                "active":active,
                "cron_status": False
        }).inserted_id
        return jsonify(ret),200

@bp.route('/list_campaign', methods=["GET"])
# @token.admin_required
def list_campaign():
        ret = mongo.db.campaigns.aggregate([
            {"$match": {"active":True}}
        ])
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
    return jsonify({"MSG":"Campaign Updated"}),200

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
                return jsonify({"MSG":"Template added to campaign"}), 200
            else:
                return jsonify({"MSG":"Template exist in campaign"}), 200
    if request.method == "DELETE":
        vac = mongo.db.campaigns.aggregate([
            { "$match": { "_id": ObjectId(campaign_id)}},
            { "$project": {"status": {"$in":[template_id,"$Template"]},"count": { "$cond": { "if": { "$isArray": "$Template" }, "then": { "$size": "$Template" }, "else": "NULL"} }}},
        ])
        vac = [serialize_doc(doc) for doc in vac]
        for data in vac:
            if data['status'] is True:
                if data['count'] >= 1:
                    ret = mongo.db.campaigns.update({"_id":ObjectId(campaign_id)},{
                        "$pull": {
                            "Template": template_id  
                        }
                    })
                    return jsonify({"MSG":"Template removed from campaign"}), 200
                else:
                    return jsonify({"MSG":"Template for the campaign cannot be none"}), 400
            else:
                return jsonify({"MSG":"Template does not exist in this campaign"}), 400


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
        return jsonify({"MSG":"Users added to campaign"}), 200  

@bp.route("/mails_status",methods=["GET"])
def mails_status():
        
    ret = mongo.db.mail_status.find({})
    ret = [serialize_doc(doc) for doc in ret]        
    return jsonify(ret), 200

# @bp.route("/template_hit_rate",methods=['GET'])
# def hit_rate():
#     template =  request.args.get('template')
#     hit = request.args.get('hit rate')
#     hit_rate_calculation = mongo.db.template.aggregate
