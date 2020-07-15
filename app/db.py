import os
from dotenv import load_dotenv
from flask_pymongo import PyMongo
from pymongo_inmemory import MongoClient

def init_db():
    mongo = PyMongo()
    return mongo


def get_db(app, mongo):
    APP_ROOT = os.path.join(os.path.dirname(__file__), '..')
    dotenv_path = os.path.join(APP_ROOT, '.env')
    load_dotenv(dotenv_path)
    if os.getenv('database'):
        print("envvvvvvvvvvvvvvvvvvvvvv")
        app.config["MONGO_URI"] = os.getenv('database')    
    else:
        print("not envvvvvvvvvvvvvvvvvvvvvvvvvv")
        client = MongoClient()  # No need to provide host
        db = client['testdb']
        collection = db['test-collection']
        # etc., etc.
        client.close()

        # Also usable with context manager
        with MongoClient() as client:
            print(client)
            print(db)
            print(collection)
            # do stuff
            app.config["MONGO_URI"] = client
    mongo.init_app(app)
