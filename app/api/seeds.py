import os
from flask import (Blueprint, flash, jsonify, abort, request, send_from_directory,redirect)
from app.util.serializer import serialize_doc
import datetime 
from app.email.model.template_making import Template_details
from app.model.campaign import campaign_details,user_data
import dateutil.parser
from app.auth import token
from flask import current_app as app
from bson.objectid import ObjectId
from app.account import initDB
from app.utils import check_and_validate_account
from app.crons import send_notification,reject_mail,campaign as campaign_crons,imap_util,calculatebounces,campaigns_details
from mail_templates import templates
from mail_variables import variables
from slack_messages import slack_message
from recruit_templates import rec_templates
from recruit_slack import rec_message

bp = Blueprint('seeds', __name__, url_prefix='/')



@bp.route('/crons/<string:type>', methods=["Post"])
@token.SecretKeyAuth
@check_and_validate_account
def master_cron(type):
    mongo = initDB(request.account_name, request.account_config)
    if type == "hr_slack_notification":    
        send_notification.cron_messages(mongo)
    if type == "recruit_notification":    
        send_notification.tms_cron_messages(mongo)
        send_notification.recruit_cron_messages(mongo)
        reject_mail.reject_mail(mongo)
        campaign_crons.MailValidator(mongo)
        campaign_crons.campaign_mail(mongo)
        imap_util.bounced_mail(mongo)
        calculatebounces.calculate_bounce_rate(mongo)
        campaigns_details.update_completion_time(mongo)
        campaigns_details.campaign_details(mongo)
        imap_util.mail_reminder(mongo)
    return jsonify({"status":"success"}),200




@bp.route('/seed_hr', methods=["GET"])
@check_and_validate_account
def seed_hr():
    mongo = initDB(request.account_name, request.account_config)
    template_exist = mongo.mail_template.find({"message_origin": "HR"})
    if template_exist:
        mongo.mail_template.remove({"message_origin":"HR"})
        mongo.mail_template.insert_many(templates)
    else:    
        mail_template = mongo.mail_template.insert_many(templates)
    mail_variable_exist = mongo.mail_variables.find({})
    if mail_variable_exist:
        mongo.mail_variables.remove({})
        mail_variable_exist = mongo.mail_variables.insert_many(variables)
    else:
        mail_variable_exist = mongo.mail_variables.insert_many(variables)

    notification_message_exist = mongo.notification_msg.find({"message_origin": "HR"})
    if notification_message_exist:
        mongo.notification_msg.remove({"message_origin": "HR"})
        mongo.notification_msg.insert_many(slack_message)
    else:
        mongo.notification_msg.insert_many(slack_message)
    return jsonify({"status":"uploaded"}),200


@bp.route('/seed_recruit', methods=["GET"])
@check_and_validate_account
def seed_recruit_data():
    mongo = initDB(request.account_name, request.account_config)
    for rec_template in rec_templates:
        template_exist = mongo.mail_template.find_one({"message_key":rec_template.get("message_key")})
        if template_exist is None:
            mongo.mail_template.insert_one(rec_template)

    for rec_messag in rec_message:
        notification_message_exist = mongo.notification_msg.find_one({"message_key":rec_messag.get("message_key")})
        if notification_message_exist is None:
            mongo.notification_msg.insert_one(rec_messag)

    for variable in variables:
        mail_variable_exist = mongo.mail_variables.find_one({"name":variable.get("name")})
        if mail_variable_exist is None:
            mongo.mail_variables.insert_one(variable)

    mail_settings_exist = mongo.mail_settings.find({"origin":"RECRUIT","active":True}).count()
    if not mail_settings_exist:
        mongo.mail_settings.insert_one({"mail_server":"smtp.sendgrid.net","mail_port":587,"origin":"RECRUIT","mail_use_tls":True,"mail_username":"apikey","mail_password":os.getenv('send_grid_key'),"active":True,"type":"tls","mail_from":"noreply@excellencetechnologies.in"})
    return jsonify({"status":"uploaded"}),200


@bp.route('/seed_system', methods=["GET"])
@check_and_validate_account
def seed_system():
    mongo = initDB(request.account_name, request.account_config)
    mail_variable_exist = mongo.mail_variables.find({})
    if mail_variable_exist:
        mongo.mail_variables.remove({})
        mail_variable_exist = mongo.mail_variables.insert_many(variables)
    else:
        mail_variable_exist = mongo.mail_variables.insert_many(variables)
    return jsonify({"status":"uploaded"}),200