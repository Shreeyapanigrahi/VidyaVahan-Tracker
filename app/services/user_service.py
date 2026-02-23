from app import db
from app.models import Trip, Vehicle
from sqlalchemy import func


class UserService:
    @staticmethod
    def _get_vehicle_ids(user_id):
        """Get all vehicle IDs for a user. Shared helper to avoid duplicate queries."""
        return [v.id for v in Vehicle.query.filter_by(user_id=user_id).with_entities(Vehicle.id).all()]

    @staticmethod
    def get_user_statistics(user_id):
        """
        Aggregate lifetime stats for the user dashboard.
        """
        vehicle_ids = UserService._get_vehicle_ids(user_id)

        if not vehicle_ids:
            return {
                "total_distance": 0,
                "total_trips": 0,
                "avg_score": 0,
                "active_vehicles": 0
            }

        stats = db.session.query(
            func.sum(Trip.total_distance_km),
            func.count(Trip.id),
            func.avg(Trip.driving_score)
        ).filter(Trip.vehicle_id.in_(vehicle_ids), Trip.status == 'completed').first()

        return {
            "total_distance": round(float(stats[0] or 0), 2),
            "total_trips": int(stats[1] or 0),
            "avg_score": round(float(stats[2] or 0), 1),
            "active_vehicles": len(vehicle_ids)
        }

    @staticmethod
    def get_recent_activity(user_id, limit=5):
        """
        Get recent completed trips across all vehicles.
        """
        vehicle_ids = UserService._get_vehicle_ids(user_id)
        if not vehicle_ids:
            return []

        return Trip.query.filter(
            Trip.vehicle_id.in_(vehicle_ids),
            Trip.status == 'completed'
        ).order_by(Trip.end_time.desc()).limit(limit).all()

    @staticmethod
    def get_active_trip(user_id):
        """
        Get the currently active trip for any of the user's vehicles.
        Crucial: Joins with Vehicle since Trip doesn't store user_id.
        """
        return Trip.query.join(Vehicle).filter(
            Vehicle.user_id == user_id,
            Trip.status == 'active'
        ).first()

