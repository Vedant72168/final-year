from flask import Flask, redirect, url_for, render_template, flash
from flask_sqlalchemy import SQLAlchemy
from config import Config
from models import db, User, ParkingSlot, VehicleEntry
from routes.auth import auth_bp
from routes.booking import booking_bp
from routes.admin import admin_bp
from flask_login import LoginManager, login_required, current_user
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize database
db.init_app(app)
with app.app_context():
    db.create_all()

# Set up Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(booking_bp, url_prefix='/booking')
app.register_blueprint(admin_bp, url_prefix='/admin')

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('landing'))
    return render_template('home.html')

@app.route('/landing')
@login_required
def landing():
    return render_template('landing.html')

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.username == 'admin':
        return redirect(url_for('admin.admin_dashboard'))
    
    db.session.expire_all()
    slots = ParkingSlot.query.all()
    vehicle_entries = VehicleEntry.query.filter_by(user_id=current_user.id).all()
    now = datetime.utcnow()
    return render_template('dashboard.html', slots=slots, vehicle_entries=vehicle_entries, now=now)

@app.route('/reserve')
@login_required
def reserve():
    available_slots = ParkingSlot.query.filter_by(status='available').all()
    return render_template('reserve.html', slots=available_slots)

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

# Static Pages
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/team')
def team():
    return render_template('team.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

# Run the app
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
