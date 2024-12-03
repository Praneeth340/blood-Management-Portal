from flask import render_template, request, redirect, url_for, session
from blood import blood
from blood.models.admin import Admin
from blood.models.donor import Donor
from blood.models.recipient import Recipient
from blood.models.appointment import Appointment
from flask import jsonify
from werkzeug.security import generate_password_hash, check_password_hash 
import logging
from bson import ObjectId
from flask import flash
from datetime import datetime
from datetime import timedelta
from blood.models.blood_donation import BloodDonations
from blood.models.blood_request import BloodRequest
from blood.models.blood_inventory import BloodInventory


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@blood.route('/create_admin', methods=['GET'])
def admin_reg():
    try:
        # Hard-coded admin data
        email = "admin@admin.com"
        user_name = "Admin User"
        phone = "123-456-7890"
        password = "admin@admin.com"

        # Check if the admin email is already registered
        if Admin.exists_by_email(email):
            return jsonify({"message": "Admin already registered. Check DB for details."}), 200

        # Data preparation
        data = {
            "user_name": user_name,
            "email": email,
            "phone": phone,
            "password": generate_password_hash(password)
        }

        # Create admin record
        Admin.create(data)
        return jsonify({"message": "Admin registered successfully!"}), 201

    except Exception as e:
        logger.error(f"Error during admin registration: {str(e)}")
        return "Internal Server Error", 500


@blood.route('/admin_home')
def admin_home():
    appointments = Appointment.get_all_pending()
    appointments = list(appointments)
    blood_requests = BloodRequest.get_all_pending()
    blood_requests = list(blood_requests)
    print(blood_requests)
    return render_template('admins/home.html', appointments=appointments, blood_requests=blood_requests)

@blood.route('/admin_manage_appointments')
def admin_manage_appointments():
    # Fetch all appointments
    appointments = Appointment.get_all()
    appointments = list(appointments)
    
    # Add donor information to each appointment
    for appointment in appointments:
        donor = Donor.get_by_id(appointment["donor_id"])  # Assuming `get_by_id` retrieves donor by ID
        # print(donor)
        appointment["donor_name"] = donor["name"]
        appointment["donor_email"] = donor["email"]
        appointment["donor_phone"] = donor["phone"]
        appointment["donor_blood_type"] = donor["blood_type"]


    return render_template('admins/manage_appointments.html', appointments=appointments)

@blood.route('/update_appointment_status/<appointment_id>', methods=['POST'])
def update_appointment_status(appointment_id):
    # Retrieve necessary information
    donor_id = Appointment.get_donor_id(appointment_id)
    blood_type = Donor.get_blood_type(donor_id)
    new_status = request.form.get('status')
    
    # Prepare data for blood donation record
    blood_data = {
        "appointment_id": appointment_id,
        "donor_id": donor_id,
        "blood_type": blood_type,
        "quantity": 1,
        "donation_date": Appointment.get_date(appointment_id),
        "request_id": ""
    }

    # Only create or update inventory if the status is marked as "Completed"
    if new_status.lower() == "completed":
        # Record the donation
        BloodDonations.create(blood_data)


        Donor.update_last_donation_date(donor_id, blood_data["donation_date"])
        Donor.update_status(donor_id, "Donated")

        # Check if inventory for this blood type already exists
        existing_inventory = BloodInventory.find_by_blood_type(blood_type)
        
        if existing_inventory:
            # Update the existing inventory
            BloodInventory.update_inventory(
                blood_type=blood_type,
                quantity_increment=1,
                donation_id=appointment_id
            )
        else:
            # Create a new inventory entry if it doesn't exist
            inventory_data = {
                "blood_type": blood_type,
                "quantity_in_units": 1,
                "donation_ids": [appointment_id]
            }
            BloodInventory.create(inventory_data)

    # Update appointment status regardless of the outcome
    Appointment.update_status(appointment_id, new_status)
    
    return redirect(url_for('admin_home'))



@blood.route('/admin_manage_donors')
def admin_manage_donors():
    try:
        # Fetch all donors
        donors = Donor.get_all()
        donors = list(donors)

        # Calculate 56 days from today
        cutoff_date = datetime.now() - timedelta(days=56)

        # Check and update eligibility based on last donation date
        for donor in donors:
            if donor['previous_donations']:
                # Convert the last donation date from string to datetime
                last_donation_date = datetime.strptime(donor['previous_donations'][-1], "%Y-%m-%d")

                # Update eligibility based on the 56-day rule
                if last_donation_date > cutoff_date:
                    donor['eligible_to_donate'] = False
                else:
                    donor['eligible_to_donate'] = True

                # Update donor in the database
                Donor.update_one(
                    {"_id": ObjectId(donor['_id'])},
                    {"$set": {"eligible_to_donate": donor['eligible_to_donate']}}
                )

        return render_template('admins/manage_donors.html', donors=donors)

    except Exception as e:
        logger.error(f"Error managing donors: {str(e)}")
        return "Internal Server Error", 500


@blood.route('/admin_manage_recipients')
def admin_manage_recipients():
    recipients = Recipient.get_all()
    recipients = list(recipients) 
    return render_template('admins/manage_recipients.html', recipients=recipients)



@blood.route('/update-donor-date', methods=['POST'])
def update_donor_date():
    data = request.json
    donor_id = data['donorId']
    donation_date = data['date']

    # Append donation date to previous_donations
    Donor.update_one(
        {"_id": ObjectId(donor_id)},
        {"$push": {"previous_donations": donation_date}}
    )

    return jsonify({"message": "Donation date updated successfully"}), 200


@blood.route('/admin_signup', methods=['GET', 'POST'])
def admin_signup():
    try: 
        if request.method == 'POST': 
            email = request.form.get("email").strip()
            if Admin.exists_by_email(email):
                return "Email already reged", 400

            password = request.form.get("password").strip()
            confirm_password = request.form.get("confirm_password").strip()

            if password != confirm_password:
                return "Passwords do not appointment", 400

            data = {
                "username": request.form.get("username").strip(),
                "email": email,
                "phone_number": request.form.get("phone").strip(),
                "password": generate_password_hash(password),
                "createdAt": datetime.now()
            } 
            Admin.create(data)
            return redirect(url_for('signin'))

        return render_template('signin_signup/admin_signup.html')
    except Exception as e:
        logger.error(f"Error during admin registration: {str(e)}")
        return "Internal Server Error", 500


@blood.route('/view_blood_request/<request_id>')
def view_blood_request(request_id):
    # Retrieve the blood request from the database by ID
    blood_request = BloodRequest.get_by_id(request_id)
    
    if not blood_request:
        flash("Blood request not found.", "error")
        return redirect(url_for('admin_home'))
    
    # Retrieve distinct blood types from the BloodInventory
    available_blood_types = BloodInventory.get_distinct_blood_types()
    print(available_blood_types)
    return render_template('admins/view_blood_request.html', blood_request=blood_request, available_blood_types=available_blood_types)


@blood.route('/get_available_quantity')
def get_available_quantity():
    blood_type = request.args.get('blood_type')
    print(f"Received blood_type: {blood_type}")  # Debug line
    inventory = BloodInventory.get_by_blood_type(blood_type)
    if inventory:
        return jsonify({"available_quantity": inventory["quantity_in_units"]})
    else:
        return jsonify({"available_quantity": 0})



@blood.route('/assign_blood/<request_id>', methods=['POST'])
def assign_blood(request_id):
    # Retrieve data from the form
    blood_type = request.form.get('blood_type')
    quantity = int(request.form.get('quantity'))
    
    # Step 1: Retrieve the blood request
    blood_request = BloodRequest.get_by_id(request_id)
    if not blood_request:
        flash("Blood request not found.", "error")
        return redirect(url_for('admin_home'))

    # Step 2: Check if there's enough quantity in the BloodInventory
    inventory = BloodInventory.get_by_blood_type(blood_type)
    if inventory and inventory["quantity_in_units"] >= quantity:
        
        # Step 3: Deduct the assigned quantity from the inventory
        new_quantity = inventory["quantity_in_units"] - quantity
        BloodInventory.update_inventory_a(blood_type=blood_type, quantity_increment=-quantity)

        # Step 4: Update the blood request status to "Completed"
        BloodRequest.update_status(request_id, "Completed")

        # Step 5: Log the assignment details (optional but recommended)
        assigned_data = {
            "request_id": request_id,
            "assigned_blood_type": blood_type,
            "assigned_quantity": quantity,
            "assigned_date": datetime.now()
        }
        # If you want, save assigned_data in a separate collection for record-keeping
        
        flash("Blood has been assigned successfully.", "success")
    else:
        flash("Insufficient blood quantity in inventory.", "error")

    return redirect(url_for('view_blood_request', request_id=request_id))

