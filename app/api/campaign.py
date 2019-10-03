from app import mongo
from flask import (Blueprint, flash, jsonify, abort, request)
from app.util import serialize_doc,Template_details
import datetime
from bson.objectid import ObjectId

bp = Blueprint('campaigns', __name__, url_prefix='/')

@bp.route('/create_campaign', methods=["GET", "POST"])
def create_campaign():
    if request.method == "GET":
        ret = mongo.db.campaigns.aggregate([])
        ret = [Template_details(serialize_doc(doc)) for doc in ret]
        return jsonify(ret)
    if request.method == "POST":
        name = request.json.get("campaign_name",None)
        description = request.json.get("campaign_description",None)
        if not name:
            return jsonify({"msg": "Invalid Request"}), 400    
        ret = mongo.db.campaigns.insert_one({
                "Campaign_name": name,
                "Campaign_description": description
        }).inserted_id
        return jsonify({"MSG":"Campaign Inserted"}),200


@bp.route('/update_campaign/<string:Id>', methods=["PUT"])
def update_campaign(Id):
    name = request.json.get("campaign_name",None)
    description = request.json.get("campaign_description",None)  
    ret = mongo.db.campaigns.update({"_id": ObjectId(Id)},{
    "$set": {
        "Campaign_name": name,
        "Campaign_description": description,
    }
    })
    return jsonify({"MSG":"Campaign Updated"}),200

@bp.route('/assign_template/<string:campaign_id>/<string:template_id>', methods=["PUT","DELETE"])
def assign_template(campaign_id,template_id):
    if request.method == "PUT":
        ret = mongo.db.campaigns.update({"_id":ObjectId(campaign_id)},{
            "$push": {
                "Template": template_id  
            }
        })
        return jsonify({"MSG":"Template added to campaign"}), 200  
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
