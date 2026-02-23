import logging
from flask import Blueprint, request, render_template, current_app
from flask_login import login_required, current_user
from app.models import Vehicle, VehicleTracking, Trip
from app.services.trip_service import TripService
from app.utils.responses import success_response, error_response
from app.utils.schemas import battery_update, trip_summary
from app import limiter

logger = logging.getLogger(__name__)

tracking = Blueprint('tracking', __name__)

# --------------- Page routes ---------------

@tracking.route('/track/<int:trip_id>')
@login_required
def live_track(trip_id):
    trip = Trip.query.filter_by(id=trip_id, status='active').first_or_404()
    vehicle = trip.vehicle
    
    if vehicle.user_id != current_user.id:
        return render_template('403.html'), 403
        
    return render_template('tracking.html', target_vehicle=vehicle, trip=trip)

@tracking.route('/view_map/<int:vehicle_id>')
@login_required
def view_map(vehicle_id):
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    if vehicle.user_id != current_user.id:
        return render_template('403.html'), 403

    trip = Trip.query.filter_by(vehicle_id=vehicle_id, status='completed') \
               .order_by(Trip.id.desc()).first()
    if not trip:
        return render_template('tracking.html', vehicle=vehicle,
                               error="No completed trip available.")

    points = VehicleTracking.query.filter_by(trip_id=trip.id) \
                 .order_by(VehicleTracking.recorded_at).all()
    coordinates = [[p.latitude, p.longitude] for p in points]
    return render_template("map.html", vehicle=vehicle, coordinates=coordinates)

@tracking.route('/trips/<int:vehicle_id>')
@login_required
def trip_history(vehicle_id):
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    if vehicle.user_id != current_user.id:
        return render_template('403.html'), 403
    trips = Trip.query.filter_by(vehicle_id=vehicle_id) \
                .order_by(Trip.start_time.desc()).all()
    return render_template('trip_history.html', vehicle=vehicle, trips=trips)

# --------------- API routes ---------------

@tracking.route('/api/update_location', methods=['POST'])
@login_required
@limiter.limit("60 per minute")
def update_location():
    data = request.get_json(silent=True) or {}
    vehicle_id = data.get('vehicle_id')
    lat = data.get('lat')
    lng = data.get('lng')

    if not all([vehicle_id, lat, lng]):
        return error_response("Missing required fields: vehicle_id, lat, lng",
                              status_code=400)

    vehicle = Vehicle.query.get(vehicle_id)
    if not vehicle or vehicle.user_id != current_user.id:
        return error_response("Unauthorized", status_code=403)

    try:
        battery = TripService.update_location(vehicle_id, lat, lng)
        return success_response(data=battery_update(battery))
    except Exception as e:
        logger.exception("update_location failed for vehicle %s", vehicle_id)
        return error_response("Location update failed", status_code=500)


@tracking.route('/api/trip/end', methods=['POST'])
@login_required
@limiter.limit("10 per minute")
def end_trip():
    data = request.get_json(silent=True) or {}
    vehicle_id = data.get('vehicle_id')

    if not vehicle_id:
        return error_response("Missing vehicle_id", status_code=400)

    vehicle = Vehicle.query.get(vehicle_id)
    if not vehicle or vehicle.user_id != current_user.id:
        return error_response("Unauthorized", status_code=403)

    try:
        trip, error = TripService.finalise_trip(vehicle_id)
        if error:
            return error_response(error)
        return success_response("Trip completed", trip_summary(trip))
    except Exception as e:
        logger.exception("end_trip failed for vehicle %s", vehicle_id)
        return error_response("Could not end trip", status_code=500)
