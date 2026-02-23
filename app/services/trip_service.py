import logging
from app import db
from app.models import Trip, VehicleTracking, BatteryStatus, Vehicle
from app.utils.simulation import haversine_distance, calculate_battery_drain
from datetime import datetime

logger = logging.getLogger(__name__)


class TripService:
    @staticmethod
    def start_trip(vehicle_id, source_id, dest_id, start_lat, start_lng, end_lat, end_lng):
        """
        Handle starting a new trip. Marks vehicle as busy.
        Ensures all non-nullable fields (campus IDs) are set before commit.
        """
        # Use row-level lock for atomic status check and update
        vehicle = Vehicle.query.filter_by(id=vehicle_id).with_for_update().first()
        if not vehicle:
            return None, "Vehicle not found"
        
        if vehicle.status == 'busy':
            return None, "Vehicle is already on another trip"

        existing = Trip.query.filter_by(vehicle_id=vehicle_id, status='active').first()
        if existing:
            return None, "Trip already active"

        try:
            # Mark vehicle as busy
            vehicle.status = 'busy'
            
            new_trip = Trip(
                vehicle_id=vehicle_id,
                source_campus_id=source_id,
                destination_campus_id=dest_id,
                start_lat=start_lat,
                start_longitude=start_lng,
                end_lat=end_lat,
                end_longitude=end_lng,
                start_time=datetime.utcnow(),
                status='active'
            )
            db.session.add(new_trip)
            db.session.commit()
            return new_trip, None
        except Exception as e:
            db.session.rollback()
            logger.exception("Failed to start trip for vehicle %s", vehicle_id)
            return None, str(e)

    @staticmethod
    def assign_and_start_trip(source_id, dest_id, start_lat, start_lng, end_lat, end_lng):
        """
        Finds the nearest available vehicle at the source location and starts a trip.
        """
        from app.services.vehicle_service import VehicleService
        
        vehicle, distance = VehicleService.get_nearest_available_vehicle(start_lat, start_lng)
        if not vehicle:
            return None, "No available vehicles nearby"
            
        return TripService.start_trip(vehicle.id, source_id, dest_id, start_lat, start_lng, end_lat, end_lng)

    @staticmethod
    def update_location(vehicle_id, lat, lng):
        """
        Update vehicle location and active trip stats.
        """
        try:
            new_track = VehicleTracking(vehicle_id=vehicle_id, latitude=lat, longitude=lng)
            db.session.add(new_track)

            active_trip = Trip.query.filter_by(vehicle_id=vehicle_id, status='active').first()
            battery = BatteryStatus.query.filter_by(vehicle_id=vehicle_id).first()

            if active_trip:
                # Assign trip_id to tracking point
                new_track.trip_id = active_trip.id

                # Use ID-based sorting for stable "previous" point retrieval
                prev_track = VehicleTracking.query.filter_by(
                    vehicle_id=vehicle_id
                ).order_by(VehicleTracking.id.desc()).offset(1).first()

                if prev_track:
                    dist = haversine_distance(prev_track.latitude, prev_track.longitude, lat, lng)
                    active_trip.total_distance_km = float(active_trip.total_distance_km or 0) + dist

                    if battery:
                        vehicle = Vehicle.query.get(vehicle_id)
                        capacity = float(vehicle.battery_capacity_kwh or 75.0)
                        drain_kwh = calculate_battery_drain(dist)
                        drain_pct = (drain_kwh / capacity) * 100 if capacity > 0 else 0
                        
                        battery.current_percentage = max(0, float(battery.current_percentage or 100) - drain_pct)
                        active_trip.battery_consumed_percent = float(active_trip.battery_consumed_percent or 0) + drain_pct

            db.session.commit()
            return battery
        except Exception:
            db.session.rollback()
            logger.exception("Failed to update location for vehicle %s", vehicle_id)
            raise

    @staticmethod
    def finalise_trip(vehicle_id):
        """
        Analyze and close the active trip.
        """
        trip = Trip.query.filter_by(vehicle_id=vehicle_id, status='active').first()
        if not trip:
            return None, "No active trip"

        try:
            vehicle = Vehicle.query.get(vehicle_id)
            if vehicle:
                vehicle.status = 'available'
                
            trip.end_time = datetime.utcnow()
            trip.status = 'completed'
            
            # Retrieve all points to determine actual end location
            points = VehicleTracking.query.filter_by(
                trip_id=trip.id
            ).order_by(VehicleTracking.recorded_at).all()

            if points:
                trip.end_lat = points[-1].latitude
                trip.end_longitude = points[-1].longitude
            else:
                trip.end_lat = trip.start_lat
                trip.end_longitude = trip.start_longitude

            # Comprehensive analysis
            capacity = vehicle.battery_capacity_kwh if vehicle else 75.0
            stats = TripService._analyze_trip_points(points, capacity)

            trip.total_distance_km = stats['total_distance']
            duration_hours = (trip.end_time - trip.start_time).total_seconds() / 3600
            trip.average_speed_kmph = round(stats['total_distance'] / duration_hours, 2) if duration_hours > 0 else 0

            trip.harsh_acceleration_count = stats['harsh_accel']
            trip.harsh_braking_count = stats['harsh_brake']
            trip.overspeed_count = stats['overspeed']

            # Scoring logic
            score = 100 - (stats['overspeed'] * 2 + stats['harsh_accel'] * 3 + stats['harsh_brake'] * 3)
            trip.driving_score = max(0, score)
            trip.driver_rating = TripService._get_rating(trip.driving_score)

            # Battery final sync
            trip.battery_consumed_percent = stats['battery_consumed_pct']

            db.session.commit()
            return trip, None
        except Exception:
            db.session.rollback()
            logger.exception("Failed to finalise trip for vehicle %s", vehicle_id)
            raise

    @staticmethod
    def _analyze_trip_points(points, battery_capacity):
        total_distance = 0
        harsh_accel = 0
        harsh_brake = 0
        overspeed = 0
        total_energy = 0

        SPEED_LIMIT = 80
        HARSH_THRESHOLD = 3
        prev_speed = 0

        for i in range(1, len(points)):
            dist = haversine_distance(
                points[i-1].latitude, points[i-1].longitude,
                points[i].latitude, points[i].longitude
            )
            total_distance += dist
            total_energy += calculate_battery_drain(dist)

            time_diff = (points[i].recorded_at - points[i-1].recorded_at).total_seconds()
            if time_diff > 0:
                speed = dist / (time_diff / 3600)
                if speed > SPEED_LIMIT:
                    overspeed += 1

                accel = (speed - prev_speed) / (time_diff / 3600) / 3600 * 1000
                if accel > HARSH_THRESHOLD:
                    harsh_accel += 1
                elif accel < -HARSH_THRESHOLD:
                    harsh_brake += 1
                prev_speed = speed

        capacity = float(battery_capacity or 75.0)
        return {
            'total_distance': round(total_distance, 2),
            'harsh_accel': harsh_accel,
            'harsh_brake': harsh_brake,
            'overspeed': overspeed,
            'battery_consumed_pct': round((total_energy / capacity) * 100, 2) if capacity > 0 else 0
        }

    @staticmethod
    def _get_rating(score):
        if score >= 85:
            return "A"
        if score >= 70:
            return "B"
        if score >= 50:
            return "C"
        return "D"

