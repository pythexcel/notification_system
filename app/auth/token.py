from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity, get_current_user, jwt_refresh_token_required,
    verify_jwt_in_request
)
from functools import wraps
from flask import (Blueprint, flash, jsonify, abort, request)
import re
import os
import sys
from flask import g, current_app, jsonify
import jwt
from bson.objectid import ObjectId

from app import mongo

from dotenv import load_dotenv

APP_ROOT = os.path.join(os.path.dirname(__file__), '..')
dotenv_path = os.path.join(APP_ROOT, '.env')
load_dotenv(dotenv_path)

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if 'Authorization' in request.headers:
            project_secret_key = request.headers.get('Authorization')
            token = project_secret_key.split()
            token = token[-1]
            user = jwt.decode(token,None,False)    
            if 'role' in user:
                if user["role"] == "Admin" or user['role'] == "HR":
                    return fn(*args, **kwargs)
                else:
                    return jsonify(msg='Unauthorized!'), 403
            else:
                if 'user_claims' in user:
                    if user["user_claims"]['role'] == "Admin" or user["user_claims"]['role'] == "HR":
                        return fn(*args, **kwargs)
                    else:
                        return jsonify(msg='Unauthorized!'), 403
        else:
            return jsonify(msg='Authorization Header Missing!'), 403
    return wrapper

def authentication(fn):
    @wraps(fn)
    def wrapp(*args, **kwargs):
        if 'Authorization' in request.headers:
            project_secret_key = request.headers.get('Authorization')        
            token = project_secret_key.split()
            token = token[-1]
            user = jwt.decode(token,None,False)   
            if 'role' in user:
                return fn(*args, **kwargs)
            else:
                if 'user_claims' in user:
                    if 'role' in user['user_claims']:
                        return fn(*args, **kwargs)
                    else:
                        return jsonify(msg='Unauthorized!'), 403
                else:
                    return jsonify(msg='Unauthorized!'), 403         
        else:
            return jsonify(msg='Authorization Header Missing!'), 403                      
    return wrapp    


def SecretKeyAuth(fn):
    @wraps(fn)
    def wrapp(*args, **kwargs):
        if 'Secretkey' in request.headers:
            project_secret_key = request.headers.get('Secretkey')        
            if "pytest" in sys.modules:
                if project_secret_key =="gUuWrJauOiLcFSDCL5TM1heITeBVcL":
                    return fn(*args, **kwargs)
                else:
                    return jsonify(msg='Unauthorized!'), 403         
            else:
                if os.getenv("SecretKey")==str(project_secret_key):
                    return fn(*args, **kwargs)
                else:
                    return jsonify(msg='Unauthorized!'), 403         
        else:
            return jsonify(msg='SecretKey Header Missing!'), 403                      
    return wrapp    
