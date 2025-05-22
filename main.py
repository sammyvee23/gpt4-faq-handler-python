from flask import Flask, redirect, url_for
from flask_login import login_required
from app.auth import auth_bp, login_manager, limiter
import os

app = Flask(__name__)

# Use environment variable for secret key (recommended)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret")

# Initialize extensions
login_manager.init_app(app)
limiter.init_app(app)

# Register blueprint
app.register_blueprint(auth_bp)

@app.route('/review')
@login_required
def review_ui():
    return "<h1>Welcome! You're logged in and viewing the review interface.</h1>"

@app.route('/')
def index():
    return redirect(url_for('auth.login'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
