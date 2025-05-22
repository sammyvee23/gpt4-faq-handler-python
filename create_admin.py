from pymongo import MongoClient
from werkzeug.security import generate_password_hash
import os

# MongoDB connection URI - change if needed
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017")

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client["call_tool"]
users = db["users"]

# Admin user info
admin_username = "adminuser"
admin_password = "ChangeMe123!"  # Change this to a strong password you want

# Hash the password
hashed_password = generate_password_hash(admin_password)

# Check if admin user already exists
existing = users.find_one({"username": admin_username})

if existing:
    print(f"User '{admin_username}' already exists.")
else:
    # Insert admin user
    users.insert_one({
        "username": admin_username,
        "password": hashed_password,
        "role": "admin",
        "email_verified": True
    })
    print(f"Admin user '{admin_username}' created with password '{admin_password}'. Please change this password after login.")
