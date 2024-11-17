# forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, DateField, TimeField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=6),
        EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
    role = SelectField('Role', choices=[('doctor', 'Doctor'), ('patient', 'Patient')], validators=[DataRequired()])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class AppointmentForm(FlaskForm):
    date = DateField('Date', validators=[DataRequired()])
    time = TimeField('Time', validators=[DataRequired()])
    submit = SubmitField('Create Appointment Slot')

class MedicalHistoryForm(FlaskForm):
    patient_id = IntegerField('Patient ID', validators=[DataRequired()])
    diagnosis = TextAreaField('Diagnosis', validators=[DataRequired()])
    submit = SubmitField('Add Medical Record')

    def validate_patient_id(self, field):
        patient = User.query.filter_by(id=field.data, role='patient').first()
        if not patient:
            raise ValidationError('Patient ID does not exist.')

class OrganDonationForm(FlaskForm):
    organ = StringField('Organ', validators=[DataRequired()])
    submit = SubmitField('Register Organ Donation')
