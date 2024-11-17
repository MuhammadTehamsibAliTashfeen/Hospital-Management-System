# models.py

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(10), nullable=False)  # 'doctor' or 'patient'

    # Relationships for Appointments
    doctor_appointments = db.relationship(
        'Appointment',
        backref='doctor',
        lazy=True,
        foreign_keys='Appointment.doctor_id'
    )
    patient_appointments = db.relationship(
        'Appointment',
        backref='patient',
        lazy=True,
        foreign_keys='Appointment.patient_id'
    )

    # Relationships for Medical Histories
    medical_histories = db.relationship(
        'MedicalHistory',
        back_populates='patient',
        lazy=True,
        foreign_keys='MedicalHistory.patient_id'
    )
    medical_notes = db.relationship(
        'MedicalHistory',
        back_populates='doctor',
        lazy=True,
        foreign_keys='MedicalHistory.doctor_id'
    )

    # Relationship for Organ Donations
    organ_donations = db.relationship(
        'OrganDonation',
        backref='donor',
        lazy=True
    )

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    status = db.Column(db.String(10), nullable=False, default='available')  # 'booked' or 'available'

class MedicalHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    diagnosis = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    # Define relationships to User model for patient and doctor
    patient = db.relationship('User', foreign_keys=[patient_id], back_populates='medical_histories')
    doctor = db.relationship('User', foreign_keys=[doctor_id], back_populates='medical_notes')

class OrganDonation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    donor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    organ = db.Column(db.String(50), nullable=False)
    availability = db.Column(db.Boolean, default=True)
