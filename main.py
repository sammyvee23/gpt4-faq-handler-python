from flask import Flask, redirect, url_for, render_template
from flask_login import login_required
from app.auth import auth_bp, login_manager, limiter
from pymongo import MongoClient
import os

app = Flask(__name__)

# Use environment variable for secret key (recommended)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret")

# Initialize Flask extensions
login_manager.init_app(app)
limiter.init_app(app)

# Register the authentication blueprint
app.register_blueprint(auth_bp)

# Connect to MongoDB Atlas with TLS enabled
mongo_uri = os.environ.get("MONGO_URI")
if not mongo_uri:
    raise RuntimeError("Missing MONGO_URI environment variable")
client = MongoClient(mongo_uri, tls=True)
db = client["Project_0"]
audit_collection = db["audit_logs"]

# Public dashboard route
@app.route('/dashboard')
def public_dashboard():
    logs = audit_collection.find().sort("timestamp", -1).limit(10)
    return render_template('dashboard.html', logs=logs)

# Logged-in dashboard route (can be re-enabled later)
@app.route('/review')
@login_required
def review_ui():
    return "<h1>Welcome! You're logged in and viewing the review interface.</h1>"

# Default homepage route redirects to dashboard
@app.route('/')
def index():
    return redirect(url_for('public_dashboard'))

# Run the Flask application
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)


