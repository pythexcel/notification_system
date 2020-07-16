from app import mongo
from flask import (Blueprint, flash, jsonify, abort, request,redirect)
from app.util.serializer import serialize_doc
from app.auth import token
from flask_jwt_extended import (JWTManager, jwt_required, create_access_token,
                                get_jwt_identity, get_current_user,
                                jwt_refresh_token_required,
                                verify_jwt_in_request)
import datetime
from app.config import slack_redirect_url,oauth_url,client_id,client_secret,client_redirect_uri,base_url
import requests 

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
    if request.method == 'POST': #If method post checking app installed or not by app code
        code = request.json.get('code')
        app_state = mongo.db.app_state.find_one({ 'code': code })
        if app_state is not None:
            return jsonify ({'message': 'app installed'})
        else:
            return jsonify ({'message': 'app not installed'})



#Api for redirect and perform authentication and store client app info into db.
#This api URL will pass as auth url in manage distribustion redirect url section in main slack app.
#Then when someone try to install our slack app he will redirect to our api here we will authenticate and will store client slack token etc inour db .

@bp.route('/redirect', methods=["GET"])
#@token.admin_required
def slack_redirect():
    #taking app code from slack shareable link
    code = request.args.get("code",default=None)
    if code is not None:
        #removing app from our db if already exists
        remove_previous_state = mongo.db.app_state.remove({'code': code})
        
        #making api url
        client_redirect_uri = base_url+'redirect'
        code_rep = oauth_url.replace("{{code}}",''+code+'')
        client_id_rep = code_rep.replace("{{client_id}}",''+client_id+'')
        client_secret_rep = client_id_rep.replace("{{client_secret}}",''+client_secret+'')
        auth_url = client_secret_rep.replace("{{redirect_uri}}",''+client_redirect_uri+'')
        
        try:
            #hitting authentication api
            token = requests.get(auth_url)
            token_resp = token.json()
            #Taking cliend slack token and other info from api response
            access_token = token_resp['access_token']
            user_token = token_resp['authed_user']['access_token']
            team = token_resp['team']
        except Exception as err:
            return(str(err)),400

        #updating slack token
        #storing app related info
        state_save = mongo.db.app_state.insert(
            {   
                'code': code,
                'slack_token':access_token,
                'slack_user_token':user_token,
                'team':team,
                'client_app_deatils':token_resp,
                'installed_on': datetime.datetime.now()
            }
        )
        return redirect(slack_redirect_url), 302 
    raise Exception("send slack auth code into param variable code")