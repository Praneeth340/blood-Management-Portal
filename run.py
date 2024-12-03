from blood import blood
from blood.controllers import admin_controller, donor_controller
from blood.controllers import signin_controller
from blood.controllers import appointment_controller, recipient_controller



if __name__ == "__main__":    
    blood.run(host='0.0.0.0', port=5001, debug=True)