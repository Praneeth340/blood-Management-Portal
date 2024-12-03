import time
from flask import render_template, request, redirect, url_for, session
from blood import blood
from blood.models.admin import Admin
from blood.models.donor import Donor
from blood.models.recipient import Recipient
from blood.models.appointment import Appointment 
from blood.models.blood_donation import BloodDonations
from datetime import time
from werkzeug.security import generate_password_hash, check_password_hash 
import logging
from bson import ObjectId
from flask import flash
from datetime import datetime
from bson import ObjectId


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)






@blood.route('/manage_appointments')
def manage_appointments():
    # Fetch all appointments for the donor from the database
    donor_id = session.get('donor_id')
    appointments = Appointment.get_by_donor(donor_id)  # Assuming this function filters appointments by donor ID
    return render_template('donors/manage_appointments.html', appointments=appointments)


@blood.route('/see_my_blood_receipts')
def see_my_blood_receipts():
    # Fetch all blood donations for the donor from the database
    donor_id = session.get('donor_id')
    blood_donations = BloodDonations.get_by_donor(donor_id)  # Assuming this function filters donations by donor ID
    return render_template('donors/blood_receipts.html', blood_donations=blood_donations)




from datetime import datetime, timedelta
from flask import jsonify, request, session, redirect, url_for, render_template, flash

@blood.route('/book_appointment', methods=['GET', 'POST'])
def book_appointment():
    donor_id = session.get('donor_id')

    # Check if there is a pending appointment
    pending_appointment = Appointment.get_pending_by_donor(donor_id)
    if pending_appointment:
        flash("You already have a pending appointment. Please delete it before booking a new one or wait for 56 days.")
        return redirect(url_for('donor_home'))

    if request.method == 'POST':
        appointment_type = request.form.get('appointment_type')
        appointment_date = request.form.get('appointment_date')
        scheduled_time = request.form.get('scheduled_time')

        # Create appointment record
        new_appointment = {
            "donor_id": donor_id,
            "appointment_type": appointment_type,
            "appointment_date": appointment_date,
            "scheduled_time": scheduled_time,
            "status": "Pending"
        }
        Appointment.create(new_appointment)
        return redirect(url_for('donor_home'))

    # Fetch all appointments for display in the dashboard
    appointments = Appointment.get_by_donor(donor_id)
    return render_template('donors/book_appointment.html', appointments=appointments)

@blood.route('/get_time_slots', methods=['POST'])
def get_time_slots():
    date = request.form.get('appointment_date')
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

@blood.route('/delete_appointment/<appointment_id>', methods=['POST'])
def delete_appointment(appointment_id):
    donor_id = session.get('donor_id')
    Appointment.delete_by_id(appointment_id, donor_id)
    flash("Appointment deleted successfully.")
    return redirect(url_for('donor_home'))
