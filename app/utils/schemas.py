"""
Schema / DTO layer.
Defines the public shape of API responses, decoupling them from
the SQLAlchemy model attributes.  If a column is renamed in the DB,
only these functions need to change — not every route or template.
"""


def trip_summary(trip):
    """Public representation of a completed trip."""
    return {
        "id": trip.id,
        "vehicle_id": trip.vehicle_id,
        "distance_km": round(float(trip.total_distance_km or 0), 2),
        "avg_speed_kmph": round(float(trip.average_speed_kmph or 0), 2),
        "battery_used_pct": round(float(trip.battery_consumed_percent or 0), 1),
        "driving_score": trip.driving_score,
        "rating": trip.driver_rating,
        "status": trip.status,
        "started_at": trip.start_time.isoformat() if trip.start_time else None,
        "ended_at": trip.end_time.isoformat() if trip.end_time else None,
    }


def vehicle_card(vehicle):
    """Public representation shown on the dashboard."""
    battery = vehicle.battery
    return {
        "id": vehicle.id,
        "name": vehicle.name,
        "license_plate": vehicle.license_plate,
        "model": vehicle.model,
        "battery_pct": round(float(battery.current_percentage), 1) if battery else 0,
    }


def battery_update(battery):
    """Real-time telemetry payload returned during live tracking."""
    if not battery:
        return {"battery": 100.0, "low_battery_alert": False}
    pct = float(battery.current_percentage)
    return {
        "battery": round(pct, 1),
        "low_battery_alert": pct < 20,
    }
