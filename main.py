from flask import Flask, redirect, url_for
from flask_login import login_required
from app.auth import auth_bp, login_manager, limiter

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # 🔒 Replace with a strong secret in production!

# Init extensions
login_manager.init_app(app)
limiter.init_app(app)

# Register auth blueprint
app.register_blueprint(auth_bp)

# Example protected route (for redirect after login)
@app.route('/review')
@login_required
def review_ui():
    return "<h1>Welcome! You're logged in and viewing the review interface.</h1>"

# Default route
@app.route('/')
def index():
    return redirect(url_for('auth.login'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

