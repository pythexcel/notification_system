from app import mongo
from flask import (Blueprint, flash, jsonify, abort, request,redirect)
from app.util import serialize_doc
from app.config import slack_redirect_url,oauth_url,client_id,client_secret,client_redirect_uri
from app import token
from flask_jwt_extended import (JWTManager, jwt_required, create_access_token,
                                get_jwt_identity, get_current_user,
                                jwt_refresh_token_required,
                                verify_jwt_in_request)

import datetime
import requests as Request

bp = Blueprint('slack_settings', __name__, url_prefix='/slack')

@bp.route('/settings', methods=['PUT', 'GET'])
#@token.admin_required
def slack_seting():
    if request.method == 'GET':
        slack = mongo.db.slack_settings.find_one({},{'_id':0})
        return jsonify(slack)

    if request.method == 'PUT':
        slack_token = request.json.get('slack_token')
        if not slack_token:
            return jsonify({'message': 'Slack Token missing'}), 400
        ret = mongo.db.slack_settings.update({}, {
            '$set': {
                'slack_token': slack_token
            }
        },upsert=True)
        return jsonify({'message':'upserted','status':True}), 200




#Api for check app installed app status how many workspaces installed our app. 
@bp.route('/app_state', methods = ['GET','POST'])
def app_state():
    if request.method == 'GET': #If method get
        availabe_app = mongo.db.app_state.find({}) #Fetching app state information from db.
        availabe_app = [serialize_doc(doc) for doc in availabe_app]
        return jsonify (availabe_app), 200
    if request.method == 'POST': #If method post checking app installed or not by app name
        app_name = request.json.get('app_name')
        app_status = mongo.db.app_state.find_one({ 'state': app_name })
        if app_state is not None:
            return jsonify ({'message': 'app installed'})
        else:
            return jsonify ({'message': 'app not installed'})


#Api for redirect and perform authentication and store info into db.
#This api URL will pass in manage distribustion redirect url section in main slack app.
#Then when someone try to install our slack app he will redirect to our api here we will authenticate and will store related info in db.
@bp.route('/redirect', methods=["GET"])
#@token.admin_required
def slack_redirect():
    code = request.args.get("code")
    state = request.args.get("state")
    remove_previous_state = mongo.db.app_state.remove({'state': state})
    #storing app related info
    state_save = mongo.db.app_state.insert(
        {   
            'state': state,
            'code': code,
            'installed_on': datetime.datetime.now()
        }
    )
    oauth_details = {
        'code': code,
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': client_redirect_uri
    }
    #hitting authentication api
    token = Request.post(oauth_url,data=oauth_details)
    token_resp = token.json().get('access_token') 
    #updating slack token
    save_token = mongo.db.slack_settings.update({}, {
        "$set": {
            "slack_token": token_resp
        }
    },upsert=True)
    return redirect(slack_redirect_url), 302 