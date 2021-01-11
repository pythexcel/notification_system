'''
from bson.objectid import ObjectId
from app.util.serializer import serialize_doc



#test for serilizer
class TestSerializeDoc:

    #Test case for if _id formate is objectid
    def test_serialize_doc(self):
        doc = {"_id":ObjectId("507f1f77bcf86cd799439011"),"data":"data"}
        serialize = serialize_doc(doc) 
        assert type(serialize['_id']) == str

    #Test case for if _id type is string
    def test_serialize_str_id(self):
        doc1 = {"_id":str("507f1f77bcf86cd799439011"),"data":"data"}
        serialize = serialize_doc(doc1) 
        assert type(serialize['_id']) == str
'''