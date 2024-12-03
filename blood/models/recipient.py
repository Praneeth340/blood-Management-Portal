from blood import mongo
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId

class Recipient:
    collection = mongo.db.recipients

    @classmethod
    def delete(cls, recipient_id):
        return cls.collection.delete_one({"_id": ObjectId(recipient_id)})
    
    @classmethod
    def get_all_pending(cls):
        return cls.collection.find({"status": "pending"})
    

    @classmethod
    def update_by_id(cls, recipient_id, data):
        return cls.collection.update_one({"_id": ObjectId(recipient_id)}, {"$set": data})
    

    @classmethod
    def update_position(cls, recipient_id, position): 
        return cls.collection.update_one({"_id": ObjectId(recipient_id)}, {"$set": {"position": position}})

    @classmethod
    def get_by_id(cls, recipient_id):
        return cls.collection.find_one({"_id": ObjectId(recipient_id)})
    

    @classmethod
    def get_all_without_team_and_same_address(cls, address): 
        return cls.collection.find({
            "team_id": None, 
            "address": {"$regex": f"^{address}$", "$options": "i"}
        })

    @classmethod
    def assign_team(cls, recipient_id, team_id):
        return cls.collection.update_one({"_id": ObjectId(recipient_id)}, {"$set": {"team_id": ObjectId(team_id)}})
    
    @classmethod
    def get_all(cls):
        return cls.collection.find()

    @classmethod
    def get_all_without_team(cls):
        return cls.collection.find({"team_id": None})

    @classmethod
    def create(cls, data):
        return cls.collection.insert_one(data)

    @classmethod
    def get_by_email(cls, email):
        return cls.collection.find_one({"email": email})

    @classmethod
    def check_password(cls, recipient, password):
        return check_password_hash(recipient["password"], password)

    @classmethod
    def exists_by_email(cls, email):
        return cls.collection.find_one({"email": email}) is not None