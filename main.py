# main.py

from flask import Flask, redirect, url_for, render_template, request, Response, flash
from flask_login import login_required, current_user
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime
from twilio.twiml.voice_response import VoiceResponse
from app.auth import auth_bp, login_manager, limiter
from app.call_handler import make_outbound_call
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret")

# Initialize Flask extensions
login_manager.init_app(app)
limiter.init_app(app)
app.register_blueprint(auth_bp)

# Connect to MongoDB (Atlas with TLS)
mongo_uri = os.environ.get("MONGO_URI")
if not mongo_uri:
    raise RuntimeError("Missing MONGO_URI environment variable")

client = MongoClient(mongo_uri, server_api=ServerApi('1'), tls=True)
try:
    client.admin.command("ping")
    print("✅ MongoDB connection successful.")
except Exception as e:
    print("❌ MongoDB connection failed:", e)

db = client["Project_0"]
audit_collection = db["audit_logs"]
users_collection = db["users"]

# ===========================
# Routes
# ===========================

@app.route('/')
def index():
    return redirect(url_for('public_dashboard'))

@app.route('/dashboard')
def public_dashboard():
    logs = audit_collection.find().sort("timestamp", -1).limit(10)
    return render_template('dashboard.html', logs=logs)

@app.route('/review')
@login_required
def review_ui():
    return "<h1>Welcome! You're logged in and viewing the review interface.</h1>"

@app.route('/test_script')
def test_script():
    from app.script_generator import generate_call_script
    test_prompt = "Call a donor and thank them for their contribution, then tell them about our next event on Friday."
    script = generate_call_script(test_prompt)
    return f"<pre>{script}</pre>"

@app.route('/twiml_script', methods=['GET'])
def twiml_script():
    script = request.args.get('text', 'Hello! This is an AI-powered call from our service. Thank you!')
    response = VoiceResponse()
    response.say(script, voice='alice')
    return Response(str(response), mimetype='text/xml')

@app.route('/make_call', methods=['GET', 'POST'])
def make_call():
    if request.method == 'POST':
        phone = request.form['phone_number']
        prompt = request.form['script']

        from app.script_generator import generate_call_script
        message = generate_call_script(prompt)
        script_url = url_for('twiml_script', text=message, _external=True)
        call_sid = make_outbound_call(phone, script_url)

        db['call_logs'].insert_one({
            'to': phone,
            'prompt': prompt,
            'generated_script': message,
            'call_sid': call_sid,
            'timestamp': datetime.utcnow()
        })

        flash(f"Call placed to {phone}. SID: {call_sid}")
        return redirect(url_for('make_call'))

    return render_template('call.html', title="Make a Phone Call")

@app.route('/call_logs')
def call_logs():
    logs = db['call_logs'].find().sort("timestamp", -1)
    return render_template('call_logs.html', logs=logs)

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']

        # Update in database
        users_collection.update_one(
            {"_id": current_user.id},
            {"$set": {"username": name, "email": email}}
        )

        flash("Settings updated!")
        return redirect(url_for('settings'))

    user = users_collection.find_one({"_id": current_user.id})
    return render_template('settings.html', title="Settings", user=user)

@app.route('/analysis')
def call_analysis():
    return render_template('analysis.html', title="Call Analysis")

# ===========================
# Run Server
# ===========================
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)



