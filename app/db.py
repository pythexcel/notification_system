from flask_pymongo import PyMongo


def init_db():
    mongo = PyMongo()
    return mongo


def get_db(app, mongo):
    app.config["MONGO_URI"] = "mongodb://hrstagingnotify:hrstagingnotify@127.0.0.1:27017/hrstagingnotify?retryWrites=true"
    mongo.init_app(app)
