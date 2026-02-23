import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise RuntimeError("SECRET_KEY environment variable is not set. Create a .env file.")

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    if not SQLALCHEMY_DATABASE_URI:
        raise RuntimeError("DATABASE_URL environment variable is not set. Create a .env file.")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session lifetime
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
    
    # CSRF token validity
    WTF_CSRF_TIME_LIMIT = 3600  # 1 hour

    # Production Security
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    # Use True if using HTTPS
    SESSION_COOKIE_SECURE = False 
    REMEMBER_COOKIE_SECURE = False

