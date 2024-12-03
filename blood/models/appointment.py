from blood import mongo
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId

class Appointment:
    collection = mongo.db.Appointments

    @classmethod
    def get_all(cls):
        return cls.collection.find()
    
    @classmethod
    def get_date(cls, appointment_id):
        return cls.collection.find_one({'_id': ObjectId(appointment_id)})['appointment_date']
    # implement get_donor_id which will return donor_id from the appointmsnts using appointment

    @classmethod
    def get_all_pending(cls):
        return cls.collection.find({'status': 'Pending'})
    @classmethod
    def get_donor_id(cls, appointment_id):
        # print("Appointment ID: ", appointment_id)
        # print("Donor ID: ", cls.collection.find_one({'_id': ObjectId(appointment_id)})['donor_id'])
        return cls.collection.find_one({'_id': ObjectId(appointment_id)})['donor_id']

    @classmethod
    def find_by_id(cls, id):
        return cls.collection.find_one({'_id': ObjectId(id)})
    
    @classmethod
    def get_by_id(cls, id):
        return cls.collection.find_one({'_id': ObjectId(id)})
    
    @classmethod
    def update_status(cls, id, status):
        cls.collection.update_one({'_id': ObjectId(id)}, {'$set': {'status': status}})
    
    @classmethod
    def update_result(cls, id, result):
        cls.collection.update_one({'_id': ObjectId(id)}, {'$set': {'result': result}})
    @classmethod
    def get_all_scheduled(cls):
        return cls.collection.find({'status': 'scheduled'})
    

    @classmethod
    def get_all_completed(cls):
        return cls.collection.find({'status': 'completed'})
    
    @classmethod
    def get_by_team_id(cls, team_id):
        return cls.collection.find({'team_id': ObjectId(team_id)})
    

    @classmethod
    def create(cls, data):
        cls.collection.insert_one(data)


    @classmethod
    def get_by_donor(cls, donor_id):
        print("Donor ID: ", donor_id)
        return cls.collection.find({'donor_id': donor_id})
        

    @classmethod
    def get_pending_by_donor(cls, donor_id):
        return cls.collection.find_one({'donor_id': donor_id, 'status': 'Pending'})
    

    @classmethod
    def delete_by_id(cls, appointment_id, donor_id):
        cls.collection.delete_one({'_id': ObjectId(appointment_id), 'donor_id': donor_id})


    @classmethod
    def update_status(cls, appointment_id, status):
        cls.collection.update_one({'_id': ObjectId(appointment_id)}, {'$set': {'status': status}})