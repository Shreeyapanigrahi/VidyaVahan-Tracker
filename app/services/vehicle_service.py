import logging
from app import db
from app.models import Vehicle, BatteryStatus

logger = logging.getLogger(__name__)


class VehicleService:
    @staticmethod
    def create_vehicle(user_id, name, license_plate, model, battery_capacity):
        """
        Handle vehicle creation logic.
        """
        try:
            vehicle = Vehicle(
                user_id=user_id,
                name=name,
                license_plate=license_plate,
                model=model,
                battery_capacity_kwh=battery_capacity
            )
            db.session.add(vehicle)
            db.session.flush()  # Get ID before commit

            # Initialize battery status
            battery = BatteryStatus(vehicle_id=vehicle.id)
            db.session.add(battery)

            db.session.commit()
            return vehicle
        except Exception:
            db.session.rollback()
            logger.exception("Failed to create vehicle for user %s", user_id)
            raise

    @staticmethod
    def get_user_vehicles(user_id):
        return Vehicle.query.filter_by(user_id=user_id).all()

    @staticmethod
    def get_vehicle_status(vehicle_id):
        vehicle = Vehicle.query.get(vehicle_id)
        if vehicle and vehicle.battery:
            return {
                "percentage": vehicle.battery.current_percentage,
                "voltage": vehicle.battery.voltage,
                "temperature": vehicle.battery.temperature
            }
        return None

    @staticmethod
    def get_nearest_available_vehicle(lat, lon):
        """
        Find the nearest vehicle with status='available' using SQLAlchemy and geopy.
        """
        from app.models import VehicleTracking
        from geopy.distance import geodesic
        from sqlalchemy import desc

        # 1. Get all available vehicles
        available_vehicles = Vehicle.query.filter_by(status='available').all()
        
        nearest_vehicle = None
        min_distance = float('inf')

        for vehicle in available_vehicles:
            # 2. Get the latest tracking point for each vehicle
            latest_point = VehicleTracking.query.filter_by(vehicle_id=vehicle.id)\
                                                .order_by(desc(VehicleTracking.recorded_at))\
                                                .first()
            
            if latest_point:
                # 3. Calculate distance using geopy
                distance = geodesic((lat, lon), (latest_point.latitude, latest_point.longitude)).kilometers
                
                if distance < min_distance:
                    min_distance = distance
                    nearest_vehicle = vehicle

        return nearest_vehicle, min_distance

