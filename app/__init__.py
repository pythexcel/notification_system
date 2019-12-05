import os

from flask import Flask, make_response, jsonify, send_from_directory, Response

from flask.cli import with_appcontext

from flask_cors import CORS

from apscheduler.schedulers.background import BackgroundScheduler

from app import db

import click

from dotenv import load_dotenv

from app.mail_templates import templates

from app.mail_variables import variables

from app.slack_messages import slack_message

mongo = db.init_db()

from app import token

from app.scheduler import campaign_mail,reject_mail,cron_messages

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True,static_url_path='')
    app.config.from_mapping()

    CORS(app)
    UPLOAD_FOLDER = os.getcwd() + '/attached_documents/'
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    APP_ROOT = os.path.join(os.path.dirname(__file__), '..')
    dotenv_path = os.path.join(APP_ROOT, '.env')
    load_dotenv(dotenv_path)
    app.config['ENV'] = os.getenv('ENVIRONMENT')

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.errorhandler(400)
    def not_found(error):
        return make_response(jsonify(error='Not found'), 400)
    
    @app.route('/pdf/<path:path>')
    def send_file(path):
        return send_from_directory('pdf', path)

    @app.errorhandler(500)
    def error_500(error):
        return make_response({}, 500)

    db.get_db(mongo=mongo, app=app)
    
    from app.api import notify
    from app.api import slack_channel
    from app.api import slack_settings
    from app.api import mail_settings
    from app.api import message_create
    from app.api import campaign
    
    app.register_blueprint(notify.bp)
    app.register_blueprint(slack_channel.bp)
    app.register_blueprint(slack_settings.bp)
    app.register_blueprint(mail_settings.bp)
    app.register_blueprint(message_create.bp)
    app.register_blueprint(campaign.bp)
    
    app.cli.add_command(seed_db)
    
    # campaign_mail_scheduler = BackgroundScheduler()
    # campaign_mail_scheduler.add_job(campaign_mail, trigger='interval', seconds=1)
    # campaign_mail_scheduler.start()

    # reject_mail_scheduler = BackgroundScheduler()
    # reject_mail_scheduler.add_job(reject_mail, trigger='interval', seconds=5)
    # reject_mail_scheduler.start()

    schduled_messages_scheduler = BackgroundScheduler()
    schduled_messages_scheduler.add_job(cron_messages,trigger='interval',seconds=1)
    schduled_messages_scheduler.start()
  
    try:
        print("create app..")
        return app
    except:
        schduled_messages_scheduler.shutdown()
        # campaign_mail_scheduler.shutdown()
        # reject_mail_scheduler.shutdown()
    
@click.command("seed_db")
@with_appcontext
def seed_db():
    template_exist = mongo.db.mail_template.find({})
    if template_exist:
        mongo.db.mail_template.remove({})
        mail_template = mongo.db.mail_template.insert_many(templates)
    else:    
        mail_template = mongo.db.mail_template.insert_many(templates)
    mail_variable_exist = mongo.db.mail_variables.find({})
    if mail_variable_exist:
        mongo.db.mail_variables.remove({})
        mail_variable_exist = mongo.db.mail_variables.insert_many(variables)
    else:
        mail_variable_exist = mongo.db.mail_variables.insert_many(variables)

    notification_message_exist = mongo.db.notification_msg.find({})
    if notification_message_exist:
        mongo.db.notification_msg.remove({})
        notification_message = mongo.db.notification_msg.insert_many(slack_message)
    else:
        notification_message = mongo.db.notification_msg.insert_many(slack_message)
    