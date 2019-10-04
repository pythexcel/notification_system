import os

from flask import Flask, make_response, jsonify, send_from_directory

from flask_cors import CORS

from apscheduler.schedulers.background import BackgroundScheduler

from app import db

mongo = db.init_db()

from app import token

jwt = token.init_token()

from app.scheduler import campaign_mail

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True,static_url_path='')
    app.config.from_mapping()
    CORS(app)
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
    def send_js(path):
        return send_from_directory('pdf', path)

    @app.errorhandler(500)
    def error_500(error):
        return make_response({}, 500)

    db.get_db(mongo=mongo, app=app)
    token.get_token(jwt=jwt, app=app)

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
    
    campaign_mail_scheduler = BackgroundScheduler()
    campaign_mail_scheduler.add_job(campaign_mail, trigger='interval', seconds=5)
    campaign_mail_scheduler.start()


    try:
        print("create app..")
        return app
    except:
        campaign_mail_scheduler.shutdown()
