# Windows Setup Instructions: EV Tracking & Monitoring System

Follow these steps to set up and run the project on your Windows machine.

## Step 1: Install Prerequisites
1. **Python**: Download and install [Python 3.10+](https://www.python.org/downloads/windows/). Ensure you check the box **"Add Python to PATH"** during installation.
2. **MySQL**: Download and install [MySQL Installer (Community)](https://dev.mysql.com/downloads/installer/). 
   - Choose "Server only" or "Developer Default".
   - Set a password for the `root` user (e.g., `password123`) and remember it.

## Step 2: Set Up the Database
1. Open **MySQL Workbench**.
2. Connect to your local instance.
3. Open the `schema.sql` file provided in the project folder.
4. Execute the script (click the Lightning icon) to create the `ev_tracking_db` database and its tables.

## Step 3: Configure the Application
1. Open the project folder in your code editor (e.g., VS Code).
2. Copy `.env.example` to `.env`:
   ```powershell
   Copy-Item .env.example .env
   ```
3. Open `.env` and update the values with your MySQL credentials:
   ```env
   DB_USER=root
   DB_PASSWORD=your_mysql_password
   DB_HOST=localhost
   DB_NAME=ev_tracking_db
   SECRET_KEY=your_secret_key_here
   DATABASE_URL=mysql+mysqlconnector://root:your_password@localhost:3306/ev_tracking_db
   ```
4. Generate a secret key by running:
   ```powershell
   python -c "import secrets; print(secrets.token_hex(16))"
   ```


## Step 4: Create a Virtual Environment (Recommended)
1. Open **Command Prompt** or **PowerShell** in the project directory.
2. Run the following commands:
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```

## Step 5: Install Dependencies
With the virtual environment active, run:
```powershell
pip install -r requirements.txt
```

## Step 6: Run the Project
Start the Flask development server:
```powershell
python run.py
```

## Step 7: Access the System
1. Open your web browser.
2. Go to `http://127.0.0.1:5000`.
3. **Registration**: Create a new user account.
4. **Dashboard**: Click "Add Vehicle" to register a new EV.
5. **Tracking**: Click "Track Live" and then "Start Trip" to see the software-based simulation in action.

---
**Note:** If you encounter any "ModuleNotFound" errors, ensure your virtual environment is activated and you have run the `pip install` command.
