from app.auth import token
#from app import mongo
from flask import (Blueprint, flash, jsonify, abort, request,url_for,send_from_directory)
from flask_jwt_extended import (JWTManager, jwt_required, create_access_token,
                                get_jwt_identity, get_current_user,
                                jwt_refresh_token_required,
                                verify_jwt_in_request)
import json
from flask import current_app as app
import dateutil.parser
import datetime
from datetime import timedelta
from app.model.interview_reminders import fetch_interview_reminders
from app.account import initDB
from app.utils import check_and_validate_account

bp = Blueprint('notify', __name__, url_prefix='/notify')



#Api for cound total reminders fron yesterday
#Not sure where this api is calling and why
#But as i read code its for return total sum of interview reminder by one day before day
@bp.route('/reminder_details/<string:jobId>', methods=["GET"])
@token.SecretKeyAuth
@check_and_validate_account
def reminder_details(jobId):
    mongo = initDB(request.account_name, request.account_config)
    date = (datetime.datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')
    before_date = dateutil.parser.parse(date)
    try:
        details = fetch_interview_reminders(mongo,date=before_date,jobId=jobId) #Here calling function for fetch interview reminder records from db by date
        if (details):
            sum = 0
            if (len(details) > 1):
                sum += details[-1]['total'] + details[-2]['total'] 
            else :
                sum +=details[-1]['total']
            return jsonify ({'total': sum}), 200
        else:
            return jsonify ({'total': 0}), 200
    except Exception as error:
        return(str(error)),400



"""
ENVIRONMENT=development
to=testingattach0@gmail.com
bcc=bcc_testing_recruit@mailinator.com
cc=cc_testing_recruit@mailinator.com
origin=recruit
database=mongodb://notify_staging:notify_staging@127.0.0.1:27017/notify_staging
base_url="http://127.0.0.1:8006/"
service=twilio
twilioSid=AC56872d72a474cee77829e5f90be39e61
twilioToken=14835448708919a666e6aba612b485f8
twilio_number=+12055129668
localtextkey=jt8iVFR027c-gUuWrJauOiLcFSDCL5TM1heITeBVcL	
SecretKey=MBw[;Rv]-6M]&3P2Grb
"""