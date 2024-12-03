from blood import mongo
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId
class BloodRequest:
    collection = mongo.db.blood_requests

    @classmethod
    def insert_one(cls, data):
        return cls.collection.insert_one(data)
    
    @classmethod
    def update_status(cls, request_id, status):
        return cls.collection.update_one({"_id": ObjectId(request_id)}, {"$set": {"status": status}})
    
    @classmethod
    def get_all_pending(cls):
        return cls.collection.find({"status": "Pending"})
    
    @classmethod
    def get_by_id(cls, request_id):
        return cls.collection.find_one({"_id": ObjectId(request_id)})


    @classmethod
    def get_all(cls):
        return cls.collection.find()
    
    @classmethod
    def get_by_recipient(cls, recipient_id):
        print(recipient_id)
        print("recipient", list(cls.collection.find({"recipient_id": recipient_id})))
        return cls.collection.find({"recipient_id": recipient_id})
    

    @classmethod
    def delete_by_id(cls, request_id):
        return cls.collection.delete_one({"_id": ObjectId(request_id)})
    
    @classmethod
    def create(cls, data):
        return cls.collection.insert_one(data)
    
    @classmethod
    def delete(cls, blood_request_id):
        return cls.collection.delete_one({"_id": ObjectId(blood_request_id)})