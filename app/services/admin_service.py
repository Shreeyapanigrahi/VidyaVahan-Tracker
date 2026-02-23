import logging
from app import db
from app.models import User, Vehicle, Trip
from sqlalchemy import func, desc

logger = logging.getLogger(__name__)


class AdminService:
    @staticmethod
    def get_dashboard_stats():
        """
        Aggregate global system statistics for the admin dashboard.
        """
        try:
            total_users = User.query.count()
            total_vehicles = Vehicle.query.count()
            total_trips = Trip.query.count()

            # Aggregate system-wide distance and average score
            stats = db.session.query(
                func.sum(Trip.total_distance_km),
                func.avg(Trip.driving_score)
            ).first()

            # Find the top-rated user based on average driving score
            # Requires joining User -> Vehicle -> Trip
            top_user = (
                db.session.query(
                    User.username,
                    func.avg(Trip.driving_score).label('avg_score')
                )
                .select_from(User)
                .join(Vehicle, Vehicle.user_id == User.id)
                .join(Trip, Trip.vehicle_id == Vehicle.id)
                .group_by(User.id)
                .order_by(desc('avg_score'))
                .first()
            )

            return {
                "success": True,
                "data": {
                    "total_users": total_users,
                    "total_vehicles": total_vehicles,
                    "total_trips": total_trips,
                    "total_distance": round(float(stats[0] or 0), 2),
                    "avg_score": round(float(stats[1] or 0), 2),
                    "top_user": top_user
                }
            }
        except Exception:
            logger.exception("Failed to load admin dashboard stats")
            return {
                "success": False,
                "error": "Could not load dashboard statistics."
            }

