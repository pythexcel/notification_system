import os
from dotenv import load_dotenv
from flask_pymongo import PyMongo
from pymongo_inmemory import MongoClient

def init_db():
    APP_ROOT = os.path.join(os.path.dirname(__file__), '..')
    dotenv_path = os.path.join(APP_ROOT, '.env')
    load_dotenv(dotenv_path)
    if os.getenv('database'):
        mongo = PyMongo()
        return mongo
    else:
        client = MongoClient()  # No need to provide host
        return client


def get_db(app, mongo):
    APP_ROOT = os.path.join(os.path.dirname(__file__), '..')
    dotenv_path = os.path.join(APP_ROOT, '.env')
    load_dotenv(dotenv_path)
    if os.getenv('database'):
        app.config["MONGO_URI"] = os.getenv('database')    
        mongo.init_app(app)
    else:
        return mongo

