from blood import mongo
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId
class Donor:
    collection = mongo.db.donors

    @classmethod
    def update_status(cls, donor_id, status):
        return cls.collection.update_one({"_id": ObjectId(donor_id)}, {"$set": {"status": status}})
        

    @classmethod
    def update_last_donation_date(cls, donor_id, last_donation_date):
        return cls.collection.update_one(
            {"_id": ObjectId(donor_id)},
            {"$push": {"previous_donations": last_donation_date}}
        )

    @classmethod
    def get_address_by_id(cls, donor_id):
        donor = cls.collection.find_one({"_id": ObjectId(donor_id)})
        return donor["address"]

    @classmethod
    def get_blood_type(cls, donor_id):
        donor = cls.collection.find_one({"_id": ObjectId(donor_id)})
        return donor["blood_type"]
    
    @classmethod
    def delete(cls, donor_id):
        return cls.collection.delete_one({"_id": ObjectId(donor_id)})

    @classmethod
    def create(cls, data):
        return cls.collection.insert_one(data)

    @classmethod
    def get_by_email(cls, email):
        return cls.collection.find_one({"email": email})

    @classmethod
    def check_password(cls, donor, password):
        return check_password_hash(donor["password"], password)

    @classmethod
    def exists_by_email(cls, email):
        return cls.collection.find_one({"email": email}) is not None
    

    @classmethod
    def get_all(cls):
        return cls.collection.find()
    
    @classmethod
    def get_by_id(cls, donor_id):
        return cls.collection.find_one({"_id": ObjectId(donor_id)})

    @classmethod
    def update(cls, donor_id, data):
        return cls.collection.update_one({"_id": ObjectId(donor_id)}, {"$set": data})


    @classmethod
    def update_one(cls, query, data):
        return cls.collection.update_one(query, data)