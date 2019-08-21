from app import mongo
from flask import (Blueprint, flash, jsonify, abort, request)
from app.slack_util import slack_message,slack_load_token
from slackclient import SlackClient

bp = Blueprint('slack_channels', __name__, url_prefix='/')


@bp.route('/slackchannels', methods=["GET"])
def slack():
    token = slack_load_token()
    print(token)
    sc = SlackClient(token)
    sl_conv_list = sc.api_call("conversations.list",
                       types="private_channel",
                       exclude_archived=True)
    sl_public_list = sc.api_call("conversations.list",
                       exclude_archived=True)

    sl_grp_list = sc.api_call("groups.list", exclude_archived=True)
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
    for elem in total:
        notSame = True
        for chnel in result:
            if ((elem["text"] == chnel["text"])
                    and (elem["value"] == chnel["value"])):
                notSame = False
        if (notSame):
            result.append(elem)
    public_channel = sl_public_list['channels']
    for details in public_channel:
        result.append({'value': details['id'], 'text': details['name']})
    return jsonify(result)