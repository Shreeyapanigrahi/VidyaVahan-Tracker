import logging
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import Trip, Vehicle, Campus, db
from app.forms import TripRequestForm
from app.services.trip_service import TripService
from datetime import datetime


logger = logging.getLogger(__name__)

trip = Blueprint('trip', __name__)

@trip.route('/request-trip', methods=['GET', 'POST'])
@login_required
def request_trip():
    form = TripRequestForm()
    campuses = Campus.query.all()
    form.source_campus.choices = [(c.id, c.name) for c in campuses]
    form.destination_campus.choices = [(c.id, c.name) for c in campuses]

    if form.validate_on_submit():
        source_id = form.source_campus.data
        dest_id = form.destination_campus.data
        
        source_campus = Campus.query.get(source_id)
        dest_campus = Campus.query.get(dest_id)

        # Find available vehicle at source campus
        vehicle = Vehicle.query.filter_by(
            campus_id=source_id, 
            status='available'
        ).first()

        if not vehicle:
            flash('No available vehicles found at the source campus.', 'danger')
            return render_template('request_trip.html', title='Request Trip', form=form)

        try:
            # Start trip via TripService logic
            # This marks vehicle busy and creates the trip atomatically with campus IDs
            new_trip, error = TripService.start_trip(
                vehicle.id, 
                source_id,
                dest_id,
                source_campus.latitude, 
                source_campus.longitude,
                dest_campus.latitude,
                dest_campus.longitude
            )
            
            if error:
                flash(error, 'danger')
                return render_template('request_trip.html', title='Request Trip', form=form)

            flash(f'Trip requested! Vehicle {vehicle.name} is assigned to you.', 'success')
            return redirect(url_for('tracking.live_track', trip_id=new_trip.id))
        except Exception as e:
            db.session.rollback()
            logger.exception("Failed to process trip request")
            flash(f'An error occurred: {str(e)}', 'danger')

    return render_template('request_trip.html', title='Request Trip', form=form)

@trip.route('/analytics')
@login_required
def analytics():
    try:
        trips = Trip.query.join(Vehicle).filter(
            Vehicle.user_id == current_user.id,
            Trip.status == 'completed'
        ).order_by(Trip.start_time).all()

        if not trips:
            return render_template("analytics.html", trips=None)

        labels = [f"Trip {i+1}" for i in range(len(trips))]
        distances = [float(t.total_distance_km or 0) for t in trips]
        speeds = [float(t.average_speed_kmph or 0) for t in trips]

        return render_template("analytics.html",
                               trips=trips,
                               labels=labels,
                               distances=distances,
                               speeds=speeds)
    except Exception as e:
        logger.exception("Failed to load analytics for user %s", current_user.id)
        return render_template("analytics.html", trips=None)

