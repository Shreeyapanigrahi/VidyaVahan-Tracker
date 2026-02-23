from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, FloatField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NumberRange
from .models import User

# ... existing forms ...

class TripRequestForm(FlaskForm):
    source_campus = SelectField('Source Campus', coerce=int, validators=[DataRequired()])
    destination_campus = SelectField('Destination Campus', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Request Trip')

    def validate_destination_campus(self, destination_campus):
        if destination_campus.data == self.source_campus.data:
            raise ValidationError('Source and destination campuses must be different.')

class RegistrationForm(FlaskForm):
    username = StringField('Username', 
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, message='Password must be at least 8 characters.')])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data.lower()).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data.lower()).first()
        if user:
            raise ValidationError('That email is already registered. Please log in.')

class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class VehicleForm(FlaskForm):
    name = StringField('Vehicle Name', validators=[DataRequired(), Length(min=2, max=50)])
    license_plate = StringField('License Plate', validators=[DataRequired(), Length(min=4, max=20)])
    model = StringField('Model', validators=[DataRequired()])
    capacity = FloatField('Battery Capacity (kWh)', validators=[DataRequired(), NumberRange(min=1, max=500, message='Capacity must be between 1 and 500 kWh.')])
    submit = SubmitField('Save Vehicle')

