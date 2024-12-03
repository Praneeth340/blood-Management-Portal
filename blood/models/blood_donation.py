from blood import mongo
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId
class BloodDonations:
    collection = mongo.db.blood_donations


    @classmethod
    def get_all(cls):
        return cls.collection.find()
    
    @classmethod
    def find_by_id(cls, id):
        return cls.collection.find_one({'_id': ObjectId(id)})
    
    @classmethod
    def create(cls, data):
        cls.collection.insert_one(data)

    @classmethod
    def get_by_donor(cls, donor_id):
        return cls.collection.find({'donor_id': donor_id})
