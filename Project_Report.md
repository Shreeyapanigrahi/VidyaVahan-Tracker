# Project Report: Software-Based Electric Vehicle Tracking and Monitoring System

**Course:** Master of Computer Applications (MCA)  
**Project Title:** Software-Based Electric Vehicle Tracking and Monitoring System  
**Language:** Python (Flask), JS, MySQL  

---

## 1. Abstract
The "Software-Based Electric Vehicle Tracking and Monitoring System" is a web application designed to simulate the tracking and monitoring of electric vehicles (EVs). Traditional tracking systems often rely heavily on hardware (GPS modules, IoT sensors), but this project focuses on a robust software-based simulation to demonstrate the logic of real-time monitoring, battery consumption modeling, and trip management. By utilizing the Haversine formula for distance calculation and a dynamic battery drain algorithm, the system provides a realistic representation of EV telematics.

## 2. Introduction
With the global shift towards sustainable energy, Electric Vehicles have become a cornerstone of modern transportation. Efficient fleet management and individual vehicle monitoring are crucial for optimizing performance and safety. This project aims to provide a centralized platform where users can register their EVs, track their live location on a map (using OpenStreetMap/Leaflet.js), monitor battery health, and analyze trip history.

## 3. Literature Survey
Wireless tracking systems have evolved from simple cellular-based triangulation to sophisticated Global Positioning Systems (GPS). Current research in EV telematics highlights the importance of "Range Anxiety" management. Systems that integrate remaining battery capacity with trip planning are highly valued. Most existing solutions are proprietary and hardware-dependent; this project explores an open-source, software-defined approach using Python and Flask.

## 4. System Analysis
### 4.1 Requirement Analysis
- **Functional Requirements:** User auth, vehicle management, live simulation, battery alerts, trip history.
- **Non-Functional Requirements:** Security (password hashing), Scalability (MySQL), Responsive UI (Bootstrap).

### 4.2 Feasibility Study
- **Technical:** High feasibility due to mature Python libraries (Flask, SQLAlchemy) and mapping APIs (Leaflet).
- **Economic:** Cost-effective as it is a software-based simulation requiring no hardware.

## 5. System Architecture
The system follows a **layered MVC** architectural pattern with a dedicated service layer:
- **Model:** SQLAlchemy classes (User, Vehicle, Trip, etc.) mapping to MySQL tables.
- **View:** Jinja2 templates (HTML/CSS) for the user interface.
- **Controller:** Flask route handlers managing request/response flow.
- **Service Layer:** Dedicated service classes encapsulating business logic, database operations, and error handling.

## 6. Database Design
The database is normalized to **Third Normal Form (3NF)** to ensure data integrity.
- **Users Table:** Stores credentials and profile data.
- **Vehicles Table:** Links vehicles to owners.
- **Trips Table:** Stores start/end coordinates and distance metrics.
- **Tracking Table:** Holds high-frequency GPS coordinate logs.
- **Battery Status Table:** Maintains real-time charge percentages.
- **Campuses Table:** Defines geographical operational zones for vehicles.
- **Ride Requests Table:** Records incoming student requests for transportation.

## 7. Implementation
### 7.1 Key Algorithms
- **Haversine Formula:** Used to calculate the distance between two GPS coordinates on a sphere.
- **Battery Drain Model:** Calculates consumption based on distance (km) and simulated vehicle efficiency.
- **GPS Simulation:** Uses random-walk scripts to simulate vehicle movement in real-time.

### 7.2 Technology Stack
- **Backend:** Python 3.x, Flask Framework.
- **Frontend:** HTML5, CSS3, JavaScript, Bootstrap 5.
- **Database:** MySQL.
- **Maps:** Leaflet.js with OpenStreetMap.

## 8. Results and Discussion
The system successfully demonstrates:
1. Secure user registration and session management.
2. Real-time visualization of vehicle movement on a web interface.
3. Automatic battery drain calculation during simulated trips.
4. Low-battery alerts triggered at a 20% threshold.
5. Persistent storage and retrieval of trip history.

## 9. Security Hardening & Production Readiness
A core focus of the development process was industrial-grade hardening:
- **Authentication Security:** Implemented `flask-bcrypt` for salted password hashing and password strength validation. Removed all hardcoded fallback secrets.
- **CSRF Protection:** Enabled global Cross-Site Request Forgery protection using `Flask-WTF`, including custom handling for AJAX `fetch` requests.
- **Rate Limiting:** Integrated `flask-limiter` to prevent brute-force attacks and API abuse on sensitive endpoints (Login, Registration, Trip Start).
- **IDOR Protection:** Implemented strict ownership verification (Authorization) on all vehicle and trip-related routes to prevent cross-user data leakage.
- **Content Security Policy (CSP):** Configured `flask-talisman` with a strict CSP to prevent Cross-Site Scripting (XSS) and data injection attacks.
- **Data Integrity:** Implemented a theoretical "Triple Layer Validation" strategy:
    1. **Frontend:** WTForms validation (type checks, length, presence).
    2. **Logic Layer:** SQLAlchemy `@validates` decorators for business rules.
    3. **Database:** MySQL `CHECK` constraints for physical data enforcement (e.g., battery 0-100%).

## 10. Quality Assurance & Reliability
- **Service Layer Pattern:** Decoupled business logic from controllers into dedicated services for better testability and maintenance.
- **Transaction Safety:** Wrapped all database commit operations in `try-except` blocks with automatic `db.session.rollback()` on failure to prevent session corruption.
- **Fail-Fast Configuration:** The application is designed to fail immediately at startup if critical environment variables (`SECRET_KEY`, `DATABASE_URL`) are missing, preventing insecure deployments.
- **Health Monitoring:** Built-in `/health` endpoint for automated monitoring of application and database connectivity.
- **Geodesic Accuracy:** Integrated `geopy` library for near-real-world distance calculations, replacing simple Euclidean math with high-precision curvature-aware telematics logic.

## 11. Conclusion
The "Software-Based EV Tracking and Monitoring System" successfully achieves its goal of simulating a telematics platform. It provides a scalable foundation for future hardware integration while serving as a powerful educational tool for understanding EV data management.


## 10. Future Scope
- **AI Integration:** Predicting range based on driving patterns.
- **API Integration:** Connecting with actual EV APIs (Tesla, Nissan Leaf).
- **Mobile App:** Developing a Flutter/React Native companion application.
- **Charging Station Locator:** Integrating OpenChargeMap API for route planning.
