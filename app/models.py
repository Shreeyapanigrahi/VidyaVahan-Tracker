from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy.orm import validates

db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='user')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    vehicles = db.relationship('Vehicle', backref='owner', lazy=True)

    @validates('email')
    def validate_email(self, key, value):
        if not value or '@' not in value:
            raise ValueError("Invalid email address")
        return value.strip().lower()

    @validates('username')
    def validate_username(self, key, value):
        if not value or len(value.strip()) < 2:
            raise ValueError("Username must be at least 2 characters")
        return value.strip().lower()

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"


class Vehicle(db.Model):
    __tablename__ = 'vehicles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    license_plate = db.Column(db.String(20), nullable=False, unique=True)
    model = db.Column(db.String(50))
    battery_capacity_kwh = db.Column(db.Float(5, 2), default=75.0)
    status = db.Column(db.Enum('available', 'busy'), default='available')
    campus_id = db.Column(db.Integer, db.ForeignKey('campuses.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    battery = db.relationship('BatteryStatus', backref='vehicle', uselist=False)
    tracking = db.relationship('VehicleTracking', backref='vehicle', lazy=True)
    trips = db.relationship('Trip', backref='vehicle', lazy=True)

    @validates('battery_capacity_kwh')
    def validate_capacity(self, key, value):
        if value is not None and value <= 0:
            raise ValueError("Battery capacity must be positive")
        return value

    def __repr__(self):
        return f"Vehicle('{self.name}', '{self.license_plate}')"

class VehicleTracking(db.Model):
    __tablename__ = 'vehicle_tracking'
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=False, index=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trips.id'), nullable=True, index=True)
    latitude = db.Column(db.Float(10, 8), nullable=False)
    longitude = db.Column(db.Float(11, 8), nullable=False)
    speed = db.Column(db.Float(5, 2), default=0.0)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f"Tracking(vehicle={self.vehicle_id}, lat={self.latitude}, lng={self.longitude})"

class BatteryStatus(db.Model):
    __tablename__ = 'battery_status'
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=False, unique=True)
    current_percentage = db.Column(db.Float(5, 2), default=100.0)
    voltage = db.Column(db.Float(5, 2))
    temperature = db.Column(db.Float(5, 2))
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @validates('current_percentage')
    def validate_percentage(self, key, value):
        if value is not None:
            value = max(0.0, min(100.0, float(value)))
        return value

    def __repr__(self):
        return f"Battery(vehicle={self.vehicle_id}, pct={self.current_percentage}%)"


class Trip(db.Model):
    __tablename__ = 'trips'

    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=False, index=True)
    source_campus_id = db.Column(db.Integer, db.ForeignKey('campuses.id'), nullable=False)
    destination_campus_id = db.Column(db.Integer, db.ForeignKey('campuses.id'), nullable=False)

    # Relationships
    source_campus = db.relationship('Campus', foreign_keys=[source_campus_id], backref='trips_from')
    destination_campus = db.relationship('Campus', foreign_keys=[destination_campus_id], backref='trips_to')

    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)

    start_lat = db.Column(db.Float(10, 8))
    start_longitude = db.Column(db.Float(11, 8))
    end_lat = db.Column(db.Float(10, 8))
    end_longitude = db.Column(db.Float(11, 8))

    total_distance_km = db.Column(db.Float(10, 2), default=0.0)
    battery_consumed_percent = db.Column(db.Float(5, 2), default=0.0)
    average_speed_kmph = db.Column(db.Float(6, 2), default=0.0)

    harsh_acceleration_count = db.Column(db.Integer, default=0)
    harsh_braking_count = db.Column(db.Integer, default=0)
    overspeed_count = db.Column(db.Integer, default=0)

    driving_score = db.Column(db.Integer)
    driver_rating = db.Column(db.String(2))

    status = db.Column(db.Enum('active', 'completed'), default='active', index=True)

    @validates('driving_score')
    def validate_score(self, key, value):
        if value is not None:
            value = max(0, min(100, int(value)))
        return value

    def __repr__(self):
        return f"Trip(id={self.id}, vehicle={self.vehicle_id}, status='{self.status}')"

class RideRequest(db.Model):
    __tablename__ = 'ride_requests'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=True)
    pickup_lat = db.Column(db.Float(10, 8), nullable=False)
    pickup_long = db.Column(db.Float(11, 8), nullable=False)
    status = db.Column(db.Enum('waiting', 'assigned', 'completed'), default='waiting', index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"RideRequest(id={self.id}, student={self.student_id}, status='{self.status}')"

class Campus(db.Model):
    __tablename__ = 'campuses'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    latitude = db.Column(db.Float(10, 8), nullable=False)
    longitude = db.Column(db.Float(11, 8), nullable=False)

    def __repr__(self):
        return f"Campus('{self.name}')"
