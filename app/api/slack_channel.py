from app import mongo
from flask import (Blueprint, flash, jsonify, abort, request)
from app.slack_util import slack_message,slack_load_token,slack_id,slack_profile
from slackclient import SlackClient
from app import token
bp = Blueprint('slack_channels', __name__, url_prefix='/')


@bp.route('/ping', methods=["GET"])
def ping():
    return jsonify ("PONG and working too :)"),200



@bp.route('/slackchannels', methods=["GET","POST"])
def slack():
    # Getting slack token from function
    token = slack_load_token()
    sc = SlackClient(token)

    if request.method == "GET":   
        # Here i am calling slack(conversations.list api for private channel)
        sl_conv_list = sc.api_call("conversations.list",
                        types="private_channel",
                        exclude_archived=True)

        # Here i am calling slack(conversations.list api for public  channel one query won't return both channels)                   
        sl_public_list = sc.api_call("conversations.list",
                        exclude_archived=True)

        # Below putting all private channels into arrays 
        inner = []
        element = sl_conv_list['channels']
        for chnl in element:
            inner.append({'value': chnl['id'], 'text': chnl['name']})

        # Below finding only public channels and putting in diffrent array to diffrentiate         
        public_chnl = []        
        public_channel = sl_public_list['channels']
        for details in public_channel:
            public_chnl.append({'value': details['id'], 'text': details['name']})
        #returning both private and public channels
        return jsonify({"Private_channel":inner,"Public_channel":public_chnl}) 

    if request.method == "POST":
        if not request.json:
            abort(500)
        #getting user slack id by using email id
        email = request.json.get("email", None)
        slack = slack_id(email)

        #getting user private channels into those channels a user and bot both exists.
        sl_user_pvt = sc.api_call(
            "users.conversations",
            types = "private_channel",
            user = slack,
            exclude_archived=True
        )

        #collecting user channels into a array.
        inner =[]            
        element = sl_user_pvt['channels']
        for details in element:
            inner.append({'value': details['id'], 'text': details['name']})

        #returning channels on those a bot can send message
        return jsonify(inner),200



@bp.route('/slack_profile', methods=["POST"])
def sl_profile():
    if not request.json:
            abort(500)
    email = request.json.get("email", None)
    try:
        slack = slack_profile(email)
        return jsonify (slack), 200
    except Exception:
        return jsonify(email),200


@bp.route('/slack_channel_ids', methods=["GET"])
def getslackid():
    token = slack_load_token()
    sc = SlackClient(token)
    sl_channel = sc.api_call(
            "im.list"
        )
    return jsonify (sl_channel),200    


@bp.route('/slack_users_list', methods=["GET"])
def getslackusers():
    token = slack_load_token()
    sc = SlackClient(token)
    sl_list = sc.api_call(
            "users.list"
        )
    return jsonify (sl_list),200    