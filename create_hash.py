from werkzeug.security import generate_password_hash

password = "admin123"  # Change this to whatever password you want to hash
hashed_password = generate_password_hash(password)
print("Your hashed password is:\n", hashed_password)
