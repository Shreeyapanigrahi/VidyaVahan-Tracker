import math
from geopy.distance import geodesic

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # Use geopy for accuracy
    return geodesic((lat1, lon1), (lat2, lon2)).kilometers

def calculate_battery_drain(distance_km, vehicle_model="Standard"):
    """
    Simulate battery consumption based on distance.
    Average consumption: 0.15 - 0.25 kWh per km for standard EVs.
    """
    avg_consumption_per_km = 0.20 # kWh per km
    return distance_km * avg_consumption_per_km

def simulate_next_location(current_lat, current_long, speed_kmh=60, direction_deg=0):
    """
    Simulate the next GPS coordinate based on speed and direction.
    """
    # Approximately 1 degree of latitude is 111km
    # This is a simplified simulation for the project
    distance_step = (speed_kmh / 3600) * 10 # 10 seconds step
    
    # Simple linear movement for simulation purposes
    # 0.0001 degrees is roughly 11 meters
    lat_step = (distance_step / 111) * math.cos(math.radians(direction_deg))
    cos_lat = math.cos(math.radians(float(current_lat)))
    if abs(cos_lat) < 1e-10:
        cos_lat = 1e-10  # Prevent division by zero near poles
    long_step = (distance_step / (111 * cos_lat)) * math.sin(math.radians(direction_deg))
    
    return float(current_lat) + lat_step, float(current_long) + long_step

