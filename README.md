# EV Tracking and Monitoring System

A software-based Electric Vehicle Tracking and Monitoring System built with Python, Flask, and MySQL.

## Prerequisites
- Python 3.8+
- MySQL Server
- `pip` (Python package installer)

## Steps to Run Locally

1. **Clone/Download the Project**
   Extract the files into a directory.

2. **Database Setup**
   - Open MySQL Workbench or your terminal.
   - Run the provided `schema.sql` script to create the database and tables.

3. **Configure Environment Variables**
   - Copy the example environment file:
     ```bash
     cp .env.example .env
     ```
   - Open `.env` and fill in your MySQL credentials and a secret key:
     ```env
     DB_USER=root
     DB_PASSWORD=your_mysql_password
     DB_HOST=localhost
     DB_NAME=ev_tracking_db
     SECRET_KEY=your_secret_key_here
     DATABASE_URL=mysql+mysqlconnector://root:your_password@localhost:3306/ev_tracking_db
     ```
   - Generate a secret key: `python -c "import secrets; print(secrets.token_hex(16))"`

4. **Create a Virtual Environment (Recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate    # Linux/macOS
   .\venv\Scripts\activate     # Windows
   ```

5. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

6. **Run the Application**
   ```bash
   python run.py
   ```
   The application will be available at `http://127.0.0.1:5000`.

7. **Run Tests (Optional)**
   ```bash
   python -m pytest
   ```
   Runs the automated smoke test suite to verify core system functionality.

8. **Production Mode (Optional)**
   ```bash
   python wsgi.py
   ```
   Uses the Waitress WSGI server on port 8080.

## Using the System
- Register a new account.
- Log in and go to **Add Vehicle**.
- Register your vehicle details.
- Click **Track Live** to see the map.
- Click **Start Trip** to begin the simulation.
- Watch as the vehicle moves, battery drains, and alerts trigger!
- Click **Stop Trip** to save the trip to history.
- Visit **Analytics** for speed and distance charts.

## Project Structure
```
project/
├── app/
│   ├── __init__.py          # App factory with extensions
│   ├── models.py            # SQLAlchemy ORM models
│   ├── forms.py             # WTForms validation
│   ├── routes/              # Blueprint controllers
│   ├── services/            # Business logic layer
│   ├── utils/               # Helpers (schemas, simulation, responses)
│   ├── templates/           # Jinja2 HTML templates
│   └── static/css/          # Stylesheets
├── config.py                # App configuration (reads from .env)
├── schema.sql               # MySQL database schema
├── run.py                   # Development server entry point
├── wsgi.py                  # Production WSGI entry point
├── requirements.txt         # Python dependencies
├── .env.example             # Environment variable template
└── .gitignore               # Git exclusion rules
```
