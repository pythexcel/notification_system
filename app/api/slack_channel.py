from app import mongo
from flask import (Blueprint, flash, jsonify, abort, request)
from app.slack_util import slack_message,slack_load_token
from slackclient import SlackClient

bp = Blueprint('slack_channels', __name__, url_prefix='/')


@bp.route('/ping', methods=["GET"])
def ping():
    return jsonify ("PONG and working too :)")


@bp.route('/slackchannels', methods=["GET"])
def slack():
    # Getting slack token from function
    token = slack_load_token()
    sc = SlackClient(token)
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


