from flask import render_template, request, redirect, url_for, session
from blood import blood
from blood.models.admin import Admin
from blood.models.donor import Donor
from blood.models.recipient import Recipient
from blood.models.appointment import Appointment
from datetime import datetime
from blood.models.blood_request import BloodRequest
from werkzeug.security import generate_password_hash, check_password_hash 
import logging
from bson import ObjectId
from flask import flash
from datetime import datetime, timedelta

from flask import jsonify
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# recipienthome
@blood.route('/recipient_home')
def recipient_home():
    blood_requests = BloodRequest.get_by_recipient(session['recipient_id'])
    blood_requests = list(blood_requests)
    return render_template('recipients/home.html', blood_requests=blood_requests)

@blood.route('/delete_blood_request/<request_id>', methods=['POST'])
def delete_blood_request(request_id):
    # Logic to delete the request based on the request_id
    BloodRequest.delete_by_id(request_id)
    flash("Your blood request has been canceled.", "success")
    return redirect(url_for('recipient_home'))



@blood.route('/signup_recipient', methods=['GET', 'POST'])
def signup_recipient(): 
    try:
        if request.method == 'POST':   
            email = request.form.get("email").strip()
            if Recipient.exists_by_email(email):
                return "Email already registered", 400

            password = request.form.get("password").strip()
            confirm_password = request.form.get("confirm_password").strip()

            if password != confirm_password:
                return "Passwords do not appointment", 400

            data = {
                "first_name": request.form.get("first_name").strip(),
                "last_name": request.form.get("last_name").strip(),
                "email": email,
                "dob": request.form.get("dob").strip(), 
                "phone_number": request.form.get("phone_number").strip(),
                "address": request.form.get("address").strip(),
                "city": request.form.get("city").strip(),
                "password": generate_password_hash(password),
                "createdAt": datetime.now(),
            } 
            Recipient.create(data)
            return redirect(url_for('signin'))

        return render_template('signin_signup/recipient_signup.html')
    except Exception as e:
        logger.error(f"Error during recipient registration: {str(e)}")
        return "Internal Server Error", 500



@blood.route('/update_recipient_profile', methods=['POST'])
def update_recipient_profile():
    recipient_id = session.get('recipient_id')
    if not recipient_id:
        return redirect(url_for('signin'))  # Redirect if no session

    # Assuming you have a function to update recipient info
    updated_info = {
        'first_name': request.form.get('first_name').strip(),
        'last_name': request.form.get('last_name').strip(),
        'email': request.form.get('email').strip(),
        'dob': request.form.get('dob').strip(),
        'phone_number': request.form.get('phone_number').strip(),
        'address': request.form.get('address').strip(),
        'city': request.form.get('city').strip(),
        'zipcode': request.form.get('zipcode').strip(),
    }

    # Update database entry
    Recipient.update_by_id(recipient_id, updated_info)
    return redirect(url_for('recipient_profile'))  # Redirect back to profile page to see updates


# @blood.route('/see_my_blood_requests')
# def see_my_blood_requests():
#     recipient_id = session.get('recipient_id')
#     if not recipient_id:
#         return redirect(url_for('signin'))

#     blood_requests = Recipient.get_blood_requests(recipient_id)
#     return render_template('recipients/blood_requests.html', blood_requests=blood_requests)


@blood.route('/request_blood', methods=['POST'])
def request_blood():
    # Retrieve recipient's ID from the session (assuming logged-in user)
    recipient_id = session.get('recipient_id')
    if not recipient_id:
        flash("You must be logged in to request blood.", "error")
        return redirect(url_for('login'))
    
    # Retrieve form data
    blood_type = request.form.get('blood_type')
    quantity = int(request.form.get('quantity'))
    scheduled_pickup_date = request.form.get('scheduled_pickup_date')
    scheduled_pickup_time = request.form.get('scheduled_pickup_time')

    # Create a new blood request entry
    blood_request = {
        "recipient_id": recipient_id,
        "blood_type": blood_type,
        "quantity": quantity,
        "requested_on": datetime.now(),
        "status": "Pending",
        "scheduled_pickup_date": scheduled_pickup_date,
        "scheduled_pickup_time": scheduled_pickup_time
    }
    
    # Save the blood request to the database
    BloodRequest.insert_one(blood_request)
    
    flash("Your blood request has been successfully submitted.", "success")
    return redirect(url_for('recipient_home'))

@blood.route('/get_time_slots_r', methods=['POST'])
def get_time_slots_r():
    date = request.form.get('scheduled_pickup_date')
    if date:
        # Generate 30-minute time slots for the selected date
        start_time = datetime.strptime("09:00", "%H:%M")
        end_time = datetime.strptime("18:00", "%H:%M")
        time_slots = []

        current_time = start_time
        while current_time <= end_time:
            time_slots.append(current_time.strftime("%H:%M"))
            current_time += timedelta(minutes=30)
        return jsonify(time_slots=time_slots)
    return jsonify(time_slots=[])
