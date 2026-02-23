import logging
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required
from app.services.vehicle_service import VehicleService
from app.forms import VehicleForm
from app import limiter

logger = logging.getLogger(__name__)
vehicle = Blueprint('vehicle', __name__)

@vehicle.route('/')
@vehicle.route('/dashboard')
@login_required
def dashboard():
    try:
        vehicles = VehicleService.get_user_vehicles(current_user.id)
    except Exception:
        logger.exception("Failed to load dashboard for user %s", current_user.id)
        flash('Could not load your vehicles. Please try again.', 'danger')
        vehicles = []
    return render_template('dashboard.html', vehicles=vehicles)

@vehicle.route('/vehicle/add', methods=['GET', 'POST'])
@login_required
@limiter.limit("5 per minute")
def add_vehicle():
    form = VehicleForm()
    if form.validate_on_submit():
        try:
            VehicleService.create_vehicle(
                user_id=current_user.id,
                name=form.name.data,
                license_plate=form.license_plate.data,
                model=form.model.data,
                battery_capacity=form.capacity.data
            )
            flash('Vehicle added successfully!', 'success')
            return redirect(url_for('vehicle.dashboard'))
        except Exception:
            logger.exception("Failed to add vehicle for user %s", current_user.id)
            flash('Error adding vehicle. Please try again.', 'danger')

    return render_template('add_vehicle.html', form=form)

