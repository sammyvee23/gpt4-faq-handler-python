from flask import Blueprint, render_template, redirect, request, url_for, flash, abort, session, Response
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
import logging
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import csv
from io import StringIO
from datetime import datetime

# === Flask-Login Setup ===
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

# === Blueprint ===
auth_bp = Blueprint('auth', __name__, template_folder='templates')

# === Rate Limiting ===
limiter = Limiter(get_remote_address)

# === MongoDB Setup ===
client = MongoClient(os.environ.get("MONGO_URI", "mongodb://localhost:27017"))
db = client["call_tool"]
user_collection = db["users"]
audit_collection = db["audit_logs"]

# === Logging Setup ===
logging.basicConfig(level=logging.INFO)

# === User Class ===
class User(UserMixin):
    def __init__(self, user_doc):
        self.id = str(user_doc['_id'])
        self.username = user_doc['username']
        self.role = user_doc.get('role', 'user')
        self.email_verified = user_doc.get('email_verified', False)

# === Load User ===
@login_manager.user_loader
def load_user(user_id):
    user_doc = user_collection.find_one({"_id": ObjectId(user_id)})
    if user_doc:
        return User(user_doc)
    return None

# === Audit Logger ===
def log_audit(action, user=None, email=None, level="info"):
    audit_collection.insert_one({
        "timestamp": datetime.utcnow(),
        "action": action,
        "user": user,
        "email": email,
        "ip": request.remote_addr,
        "user_agent": request.headers.get('User-Agent'),
        "level": level
    })

# === Login Route ===
@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_doc = user_collection.find_one({"username": username})
        if user_doc and check_password_hash(user_doc['password'], password):
            if not user_doc.get('email_verified', False):
                flash('Please verify your email before logging in.')
                return redirect(url_for('auth.login'))
            login_user(User(user_doc))
            session['role'] = user_doc.get('role', 'user')
            log_audit("login_success", username, level="info")
            return redirect(url_for('review_ui'))
        flash('Invalid credentials')
        log_audit("login_failed", username, level="warning")
    return render_template('login.html')

# === Create User Route (Admins Only) ===
@auth_bp.route('/create_user', methods=['GET', 'POST'])
@login_required
def create_user():
    if current_user.role != 'admin':
        abort(403)

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        role = request.form.get('role', 'user')

        if user_collection.find_one({"username": username}):
            flash('Username already exists.')
            return redirect(url_for('auth.create_user'))

        hashed_pw = generate_password_hash(password)
        user_collection.insert_one({
            "username": username,
            "password": hashed_pw,
            "email": email,
            "role": role,
            "email_verified": True
        })
        flash('User created successfully!')
        log_audit("user_created", user=current_user.username, email=username)
        return redirect(url_for('auth.create_user'))

    return render_template('create_user.html')

# === Audit Log View (Admins Only) ===
@auth_bp.route('/admin/audit_logs')
@login_required
def audit_logs():
    if current_user.role != 'admin':
        abort(403)
    query = {}
    if request.args.get('user'):
        query['user'] = request.args['user']
    if request.args.get('action'):
        query['action'] = request.args['action']
    logs = audit_collection.find(query).sort("timestamp", -1).limit(100)
    return render_template('audit_logs.html', logs=logs)

# === Export Logs to CSV (Admins Only) ===
@auth_bp.route('/admin/export_logs')
@login_required
def export_logs():
    if current_user.role != 'admin':
        abort(403)
    logs = audit_collection.find().sort("timestamp", -1)
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['Timestamp', 'Action', 'User', 'Email', 'IP', 'User Agent', 'Level'])
    for log in logs:
        writer.writerow([
            log.get('timestamp', ''),
            log.get('action', ''),
            log.get('user', ''),
            log.get('email', ''),
            log.get('ip', ''),
            log.get('user_agent', ''),
            log.get('level', 'info')
        ])
    output.seek(0)
    return Response(output, mimetype="text/csv", headers={"Content-Disposition": "attachment;filename=audit_logs.csv"})

