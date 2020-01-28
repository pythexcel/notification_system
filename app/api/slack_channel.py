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
        # Here i am calling slack(group.list api for private channel as on our main slack some channels not come from above api)
        sl_grp_list = sc.api_call("groups.list", exclude_archived=True)
        # Below putting all the channels in two arrays then merging in total variable 
        channel = []
        detail = sl_grp_list['groups']
        for grp in detail:
            channel.append({'value': grp['id'], 'text': grp['name']})
        inner = []
        element = sl_conv_list['channels']
        for chnl in element:
            inner.append({'value': chnl['id'], 'text': chnl['name']})
        total = inner + channel
        result = []
        # Below in Total some channels have some duplicate channels remove them 
        for elem in total:
            notSame = True
            for chnel in result:
                if ((elem["text"] == chnel["text"])
                        and (elem["value"] == chnel["value"])):
                    notSame = False
            if (notSame):
                result.append(elem)
        # Below finding only public channels and putting in diffrent array to diffrentiate         
        public_chnl = []        
        public_channel = sl_public_list['channels']
        for details in public_channel:
            public_chnl.append({'value': details['id'], 'text': details['name']})
        return jsonify({"Private_channel":total,"Public_channel":public_chnl}) 
    else:
        if not request.json:
            abort(500)
        email = request.json.get("email", None)
        slack = slack_id(email)
        sl_user_pvt = sc.api_call(
            "users.conversations",
            types = "private_channel",
            user = slack,
            exclude_archived=True
        )
        sl_user_private = sc.api_call(
            "groups.list",
            exclude_archived=True
        )
        channel = []
        detail = sl_user_private['groups']
        for data in detail:
            if slack in data['members']:
                channel.append({'value': data['id'], 'text': data['name']})
        inner =[]            
        element = sl_user_pvt['channels']
        for details in element:
            inner.append({'value': details['id'], 'text': details['name']})
        total = inner + channel
        result = []
        for elem in total:
            notSame = True
            for dec in result:
                if ((elem["text"] == dec["text"]) and (elem["value"] == dec["value"])):
                    notSame =False
            if (notSame):
                result.append(elem)
        return jsonify(result),200


@bp.route('/slack_profile', methods=["POST"])
def sl_profile():
    if not request.json:
            abort(500)
    email = request.json.get("email", None)
    print(email)
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
