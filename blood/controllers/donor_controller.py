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



@blood.route('/donor_home')
def donor_home():
    appointments = Appointment.get_by_donor(session['donor_id'])
    return render_template('donors/home.html',appointments=appointments)


from datetime import datetime, timedelta

@blood.route('/signup_donor', methods=['GET', 'POST'])
def signup_donor():
    try:
        if request.method == 'POST':
            name = request.form.get("name").strip()
            email = request.form.get("email").strip()
            password = request.form.get("password").strip()
            confirm_password = request.form.get("confirm_password").strip()
            phone = request.form.get("phone").strip()
            address = request.form.get("address").strip()
            blood_type = request.form.get("blood_type").strip()
            previous_donations = request.form.getlist("previous_donations")  # List of previous donation dates
            
            # Validate email uniqueness
            if Donor.exists_by_email(email):
                return "Email already registered", 400

            # Validate password matching
            if password != confirm_password:
                return "Passwords do not match", 400

            # Convert previous donations to datetime objects
            previous_donation_dates = [datetime.strptime(date.strip(), '%Y-%m-%d') for date in previous_donations if date.strip()]
            
            # Determine the eligibility based on the last donation date
            if previous_donation_dates:
                last_donation_date = max(previous_donation_dates)
                eligible_to_donate = datetime.now() >= last_donation_date + timedelta(days=56)
            else:
                eligible_to_donate = True

            data = {
                "name": name,
                "email": email,
                "password": generate_password_hash(password),
                "phone": phone,
                "address": address,
                "blood_type": blood_type,
                "previous_donations": previous_donation_dates,
                "eligible_to_donate": eligible_to_donate,
                "createdAt": datetime.now(),
                "status": "Active"
            }
            Donor.create(data)
            return redirect(url_for('signin'))

        return render_template('signin_signup/donor_signup.html')
    except Exception as e:
        logger.error(f"Error during donor registration: {str(e)}")
        return "Internal Server Error", 500
