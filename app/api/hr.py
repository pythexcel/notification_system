from flask import (
   Blueprint, g, request, abort, jsonify)
from app import mongo
from flask_jwt_extended import (
    jwt_required, create_access_token, get_current_user
)
from bson import ObjectId
import datetime
from dateutil.relativedelta import relativedelta


bp = Blueprint('hr', __name__, url_prefix='/hr')


@bp.route('/settings', methods=['POST'])
@jwt_required
def tms_update():

    user = get_current_user()
    return ("settings off")

   
