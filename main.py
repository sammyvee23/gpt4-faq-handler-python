from flask import Flask, redirect, url_for, render_template
from flask_login import login_required
from app.auth import auth_bp, login_manager, limiter
from pymongo import MongoClient
from datetime import datetime
from flask import flash
from flask import request, Response
from twilio.twiml.voice_response import VoiceResponse
from app.call_handler import make_outbound_call
from dotenv import load_dotenv
load_dotenv()

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

@app.route('/test_script')
def test_script():
    from app.script_generator import generate_call_script
    test_prompt = "Call a donor and thank them for their contribution, then tell them about our next event on Friday."
    script = generate_call_script(test_prompt)
    return f"<pre>{script}</pre>"

@app.route('/twiml_script', methods=['POST', 'GET'])
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
        
        # Optional: AI-enhanced message
        from app.script_generator import generate_call_script
        message = generate_call_script(prompt)

        # Generate TwiML URL
        script_url = url_for('twiml_script', text=message, _external=True)

        # Make the call
        call_sid = make_outbound_call(phone, script_url)

        # Save to MongoDB
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

@app.route('/settings')
def settings():
    return render_template('settings.html', title="Settings")

@app.route('/analysis')
def call_analysis():
    return render_template('analysis.html', title="Call Analysis")

@app.route('/make_call', methods=['GET', 'POST'])
def make_call():
    if request.method == 'POST':
        phone = request.form['phone_number']
        script = request.form['script']
        # TODO: Trigger Twilio or Vonage API call
        flash(f"Call to {phone} queued with script.")
        return redirect(url_for('make_call'))
    return render_template('call.html', title="Make a Phone Call")

# Run the Flask application
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)


