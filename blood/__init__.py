
from flask import Flask
from flask_pymongo import PyMongo
from flask_jwt_extended import JWTManager 



blood = Flask(__name__, template_folder='views', static_folder='static')
blood.config["MONGO_URI"] = "mongodb://localhost:27017/blood2"
blood.config['JWT_SECRET_KEY'] = "blooddonation"


blood.secret_key = "adb"

mongo = PyMongo(blood)
jwt = JWTManager(blood)
    
    