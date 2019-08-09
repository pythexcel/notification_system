from flask import (Blueprint, g, request, abort, jsonify)
import jwt
from flask_jwt_extended import (jwt_required, create_access_token,
                                get_current_user)
import re
from bson.objectid import ObjectId
import requests
import datetime
from app.config import URL, URL_details
from app import mongo
from app import token
import dateutil.parser

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/login', methods=['POST'])
def login():
    print("login")
    log_username = request.json.get("username", None)
    print(log_username)
    password = request.json.get("password", None)
    if not log_username:
        return jsonify(msg="Missing username parameter"), 400
    if not password:
        return jsonify(msg="Missing password parameter"), 400

    payload_user_login = {
        'username': log_username,
        "password": password,
        "action": "login",
        "token": None
    }
    response_user_token = requests.post(url=URL, json=payload_user_login)
    token = response_user_token.json()
    if token['data'] == {'message': 'Invalid Login'}:
        return jsonify(msg='invalid login'), 500
    else:
        role_response = jwt.decode(token['data']['token'], None, False)
        if role_response["role"] == "Admin":
            username = log_username
            user = mongo.db.users.find_one({"username": username})
            print("MONGO DATABASE RESPONSE")
            print(user)
            if user is not None:
                print('user exists so updating')
                mongo.db.users.update({"username": username}, {
                    "$set": {
                        "username": username,
                        "last_login": datetime.datetime.now()
                    }
                })
            else:
                print('admin role')
                role = "Admin"
                mongo.db.users.insert_one({
                    "username": username,
                    "last_login": datetime.datetime.now(),
                    "role": role
                }).inserted_id
            username1 = log_username
            print(username1)
            print('User token generated for user')
            expires = datetime.timedelta(days=1)
            access_token = create_access_token(identity=username1,
                                               expires_delta=expires)
            return jsonify(access_token=access_token), 200
        else:
            return jsonify({"msg": "INVALID LOGIN"}), 404


@bp.route('/dota', methods=['GET'])
def protected():
    return jsonify("@2"), 200


@bp.route('/profile', methods=['GET'])
@jwt_required
def profile():
    current_user = get_current_user()
    ret = mongo.db.users.find_one({"_id": ObjectId(current_user["_id"])})
    ret["_id"] = str(ret["_id"])
    return jsonify(ret)
