from flask import Flask, redirect, url_for, render_template
from flask_login import login_required
from app.auth import auth_bp, login_manager, limiter
from pymongo import MongoClient
import os

app = Flask(__name__)

# Use environment variable for secret key (recommended)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret")

# Initialize extensions
login_manager.init_app(app)
limiter.init_app(app)

# Register blueprint
app.register_blueprint(auth_bp)

# Connect to MongoDB
client = MongoClient(os.environ.get("MONGO_URI", "mongodb://localhost:27017"))
db = client["call_tool"]
audit_collection = db["audit_logs"]

# Public dashboard route
@app.route('/dashboard')
def public_dashboard():
    logs = audit_collection.find().sort("timestamp", -1).limit(10)
    return render_template('dashboard.html', logs=logs)

# Logged-in dashboard (still works if you enable login later)
@app.route('/review')
@login_required
def review_ui():
    return "<h1>Welcome! You're logged in and viewing the review interface.</h1>"

# Homepage route (update if you want to skip login temporarily)
@app.route('/')
def index():
    return redirect(url_for('public_dashboard'))  # now redirects to public dashboard

# Run the Flask app
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
