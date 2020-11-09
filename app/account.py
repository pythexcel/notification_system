has_mongo = False
try:
    from pymongo import MongoClient
    from bson.objectid import ObjectId
    has_mongo = True   
except ModuleNotFoundError as e:
    pass

db_hosts = {}
def initDB(account_name, account_config):
    if not has_mongo:
        return None
        
    global db_hosts
    if account_name not in db_hosts:
        client = MongoClient(account_config["mongodb"]["host"])
        db_hosts[account_name] = client[account_config["mongodb"]["db"]]


    return db_hosts[account_name]
