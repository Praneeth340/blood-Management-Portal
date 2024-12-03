from werkzeug.security import generate_password_hash

# The password to be hashed
password = "admin@admin.com"

# Generate hashed password
hashed_password = generate_password_hash(password)

print(f"Hashed Password: {hashed_password}")
