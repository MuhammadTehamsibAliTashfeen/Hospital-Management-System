# app.py

from flask import Flask, render_template, redirect, url_for, request, flash
from models import db, User, Appointment, MedicalHistory, OrganDonation
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from forms import LoginForm, RegistrationForm, AppointmentForm, MedicalHistoryForm, OrganDonationForm
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy.orm import joinedload
from flask_wtf import CSRFProtect

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Replace with your actual secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

csrf = CSRFProtect(app)
db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Context processor to inject csrf_token into templates
from flask_wtf.csrf import generate_csrf

@app.context_processor
def inject_csrf_token():
    return dict(csrf_token=generate_csrf())

@app.route('/')
def home():
    return render_template('home.html')

# Registration Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)  # Default method is pbkdf2:sha256
        new_user = User(username=form.username.data, password=hashed_password, role=form.role.data)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration Successful! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('Logged in Successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid Username or Password', 'danger')
    return render_template('login.html', form=form)

# Dashboard Route
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

# Logout Route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

# Appointment Booking
@app.route('/appointments', methods=['GET', 'POST'])
@login_required
def appointments():
    if current_user.role == 'doctor':
        form = AppointmentForm()
        if form.validate_on_submit():
            new_appointment = Appointment(
                doctor_id=current_user.id,
                date=form.date.data,
                time=form.time.data,
                status='available'
            )
            db.session.add(new_appointment)
            db.session.commit()
            flash('Appointment Slot Created!', 'success')
            return redirect(url_for('appointments'))
        appointments = Appointment.query.filter_by(doctor_id=current_user.id).options(joinedload(Appointment.patient)).all()
        return render_template('appointment.html', form=form, appointments=appointments)
    elif current_user.role == 'patient':
        # Fetch patient's booked appointments
        booked_appointments = Appointment.query.filter_by(patient_id=current_user.id).options(joinedload(Appointment.doctor)).all()
        # Fetch available appointments
        available_appointments = Appointment.query.filter_by(status='available').options(joinedload(Appointment.doctor)).all()
        return render_template(
            'appointment.html',
            booked_appointments=booked_appointments,
            available_appointments=available_appointments
        )
    else:
        flash('Invalid Role', 'danger')
        return redirect(url_for('dashboard'))

@app.route('/book_appointment/<int:appointment_id>')
@login_required
def book_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    if appointment.status == 'available':
        appointment.patient_id = current_user.id
        appointment.status = 'booked'
        db.session.commit()
        flash('Appointment Booked!', 'success')
    else:
        flash('Appointment Not Available', 'danger')
    return redirect(url_for('appointments'))

# Medical History
@app.route('/medical_history', methods=['GET', 'POST'])
@login_required
def medical_history():
    if current_user.role == 'doctor':
        form = MedicalHistoryForm()
        if form.validate_on_submit():
            new_history = MedicalHistory(
                patient_id=form.patient_id.data,
                doctor_id=current_user.id,
                diagnosis=form.diagnosis.data
            )
            db.session.add(new_history)
            db.session.commit()
            flash('Medical History Updated!', 'success')
            return redirect(url_for('medical_history'))
        histories = current_user.medical_notes
        return render_template('medical_history.html', form=form, histories=histories)
    elif current_user.role == 'patient':
        histories = current_user.medical_histories
        return render_template('medical_history.html', histories=histories)
    else:
        flash('Invalid Role', 'danger')
        return redirect(url_for('dashboard'))

# Organ Donation
@app.route('/organ_donation', methods=['GET', 'POST'])
@login_required
def organ_donation():
    form = OrganDonationForm()
    if form.validate_on_submit():
        new_donation = OrganDonation(
            donor_id=current_user.id,
            organ=form.organ.data,
            availability=True
        )
        db.session.add(new_donation)
        db.session.commit()
        flash('Organ Donation Registered!', 'success')
        return redirect(url_for('organ_donation'))
    donations = OrganDonation.query.filter_by(availability=True).all()
    return render_template('organ_donation.html', form=form, donations=donations)

# Search for Organs
@app.route('/search_organ', methods=['GET'])
@login_required
def search_organ():
    organ = request.args.get('organ')
    if organ:
        donations = OrganDonation.query.filter_by(organ=organ, availability=True).all()
        return render_template('organ_donation.html', donations=donations)
    else:
        flash('Please enter an organ to search.', 'warning')
        return redirect(url_for('organ_donation'))
    
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
