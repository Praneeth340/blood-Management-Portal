from flask import render_template, request, redirect, url_for, session
from blood import blood
from blood.models.admin import Admin
from blood.models.donor import Donor
from blood.models.recipient import Recipient
from blood.models.appointment import Appointment

from werkzeug.security import generate_password_hash, check_password_hash 
import logging
from bson import ObjectId
from flask import flash
from datetime import datetime


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



@blood.route('/',)
def home():
    return render_template('index.html')











@blood.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST': 
        email = request.form.get("email").strip()   
        password = request.form.get("password").strip()
        if Recipient.exists_by_email(email):
            recipient = Recipient.get_by_email(email)
            if check_password_hash(recipient['password'], password):
                session["recipient_id"] = str(recipient['_id'])
                session["recipient_type"] = "recipient"
                return redirect(url_for('recipient_home'))
            else:
                return "Invalid credentials", 400
            
        elif Donor.exists_by_email(email):
            donor = Donor.get_by_email(email)
            if donor['status'] == "Pending":
                return "Account pending approval. Please wait for an administrator to activate your account.", 403
            if check_password_hash(donor['password'], password):
                session["donor_id"] = str(donor['_id'])
                session["donor_type"] = "donor"
                return redirect(url_for('donor_home'))
            else:
                return "Invalid credentials", 400

        # check if admin exists in the admin database
        elif Admin.exists_by_email(email):
            admin = Admin.get_by_email(email)
            if check_password_hash(admin['password'], password):
                session["admin_id"] = str(admin['_id'])
                session["admin_type"] = "admin"
                return redirect(url_for('admin_home'))
            else:
                return "Invalid credentials", 400

    return render_template('signin_signup/signin.html')



@blood.route('/logout')
def logout():
    try:
        session.pop('recipient_id', None)
        session.pop('recipient_type', None)
        session.pop('donor_id', None)
        session.pop('donor_type', None)
        session.pop('admin_id', None)
        session.pop('admin_type', None)
        return redirect(url_for('signin'))
    except Exception as e:
        logger.error(f"Error during logout: {str(e)}")
        return "Internal Server Error", 500

