-- Database Creation Script for EV Tracking and Monitoring System
-- Table order: users → vehicles → battery_status → trips → vehicle_tracking
-- (Dependencies must be created before dependents)

CREATE DATABASE IF NOT EXISTS ev_tracking_db;
USE ev_tracking_db;

-- ================== 1. USERS ==================
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ================== 2. VEHICLES ==================
CREATE TABLE IF NOT EXISTS vehicles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    license_plate VARCHAR(20) NOT NULL UNIQUE,
    model VARCHAR(50),
    battery_capacity_kwh DECIMAL(5, 2) DEFAULT 75.0 CHECK (battery_capacity_kwh > 0),
    status ENUM('available', 'busy') DEFAULT 'available',
    campus_id INT NULL,
    battery_level FLOAT DEFAULT 100.0 CHECK (battery_level BETWEEN 0 AND 100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (campus_id) REFERENCES campuses(id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- ================== 3. BATTERY STATUS ==================
CREATE TABLE IF NOT EXISTS battery_status (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vehicle_id INT NOT NULL UNIQUE,
    current_percentage DECIMAL(5, 2) DEFAULT 100.0 CHECK (current_percentage >= 0 AND current_percentage <= 100),
    voltage DECIMAL(5, 2),
    temperature DECIMAL(5, 2),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ================== 4. TRIPS ==================
-- Must come BEFORE vehicle_tracking (tracking references trips.id)
CREATE TABLE IF NOT EXISTS trips (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vehicle_id INT NOT NULL,
    source_campus_id INT NOT NULL,
    destination_campus_id INT NOT NULL,
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP NULL,
    start_lat DECIMAL(10, 8),
    start_longitude DECIMAL(11, 8),
    end_lat DECIMAL(10, 8),
    end_longitude DECIMAL(11, 8),
    total_distance_km DECIMAL(10, 2) DEFAULT 0.0 CHECK (total_distance_km >= 0),
    battery_consumed_percent DECIMAL(5, 2) DEFAULT 0.0 CHECK (battery_consumed_percent >= 0),
    average_speed_kmph DECIMAL(6, 2) DEFAULT 0.0 CHECK (average_speed_kmph >= 0),
    harsh_acceleration_count INT DEFAULT 0,
    harsh_braking_count INT DEFAULT 0,
    overspeed_count INT DEFAULT 0,
    driving_score INT DEFAULT 100 CHECK (driving_score >= 0 AND driving_score <= 100),
    driver_rating VARCHAR(2),
    status ENUM('active', 'completed') DEFAULT 'active',
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(id) ON DELETE CASCADE,
    FOREIGN KEY (source_campus_id) REFERENCES campuses(id) ON DELETE SET NULL,
    FOREIGN KEY (destination_campus_id) REFERENCES campuses(id) ON DELETE SET NULL,
    INDEX idx_trips_vehicle (vehicle_id),
    INDEX idx_trips_status (status)
) ENGINE=InnoDB;

-- ================== 5. VEHICLE TRACKING ==================
CREATE TABLE IF NOT EXISTS vehicle_tracking (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vehicle_id INT NOT NULL,
    trip_id INT NULL,
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    speed DECIMAL(5, 2) DEFAULT 0.0,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(id) ON DELETE CASCADE,
    FOREIGN KEY (trip_id) REFERENCES trips(id) ON DELETE CASCADE,
    INDEX idx_tracking_vehicle (vehicle_id),
    INDEX idx_tracking_trip (trip_id),
    INDEX idx_tracking_time (recorded_at)
) ENGINE=InnoDB;

