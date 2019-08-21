from app import mongo
import requests


def serialize_doc(doc):
    doc["_id"] = str(doc["_id"])
    return doc