from blood import mongo
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId
class BloodInventory:
    collection = mongo.db.blood_inventory


    @classmethod
    def get_distinct_blood_types(cls):
        return cls.collection.distinct("blood_type")

    @classmethod
    def update_inventory(cls,blood_type, quantity_increment, donation_id):
        # Increment quantity and add donation_id to the list
        cls.update_one(
            {"blood_type": blood_type},
            {
                "$inc": {"quantity_in_units": quantity_increment},
                "$push": {"donation_ids": donation_id}
            }
        )

    @classmethod
    def update_inventory_a(cls, blood_type, quantity_increment):
        cls.update_one(
            {"blood_type": blood_type},
            {"$inc": {"quantity_in_units": quantity_increment}}
        )

    @classmethod
    def find_by_blood_type(cls, blood_type):
        return cls.collection.find_one({"blood_type": blood_type})
    @classmethod
    def get_all(cls):
        return cls.collection.find()
    
    @classmethod
    def get_by_id(cls, blood_inventory_id):
        return cls.collection.find_one({"_id": ObjectId(blood_inventory_id)})

    @classmethod
    def get_by_blood_type(cls, blood_type):
        print(blood_type)
        return cls.collection.find_one({"blood_type": blood_type})
    
    @classmethod
    def create(cls, data):
        return cls.collection.insert_one(data)

    @classmethod
    def delete(cls, blood_inventory_id):
        return cls.collection.delete_one({"_id": ObjectId(blood_inventory_id)})

    @classmethod
    def update(cls, blood_inventory_id, data):
        return cls.collection.update_one({"_id": ObjectId(blood_inventory_id)}, {"$set": data})

    @classmethod
    def update_one(cls, query, data):
        return cls.collection.update_one(query, data)