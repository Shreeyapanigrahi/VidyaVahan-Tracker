from flask import Flask, render_template
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_talisman import Talisman
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect
from .models import db, User
from config import Config
import logging
from logging.handlers import RotatingFileHandler
import os

bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

limiter = Limiter(key_func=get_remote_address, default_limits=["200 per day", "50 per hour"])
csrf = CSRFProtect()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    limiter.init_app(app)
    csrf.init_app(app)

    # Logging Configuration
    if not app.debug:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/ev_tracking.log', maxBytes=1048576, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('EV Tracking Startup')

    # Security: Flask-Talisman
    csp = {
        'default-src': '\'self\'',
        'script-src': [
            '\'self\'',
            'https://cdn.jsdelivr.net',
            'https://unpkg.com',
            '\'unsafe-inline\''  # Required for Chart.js/Leaflet setup scripts
        ],
        'style-src': [
            '\'self\'',
            'https://cdn.jsdelivr.net',
            'https://unpkg.com',
            'https://cdnjs.cloudflare.com',
            '\'unsafe-inline\''
        ],
        'font-src': [
            '\'self\'',
            'https://cdnjs.cloudflare.com'
        ],
        'img-src': ['\'self\'', 'https://*.tile.openstreetmap.org', 'data:']
    }
    Talisman(app, content_security_policy=csp, force_https=False)  # Set force_https=True in real production

    # Register Blueprints
    from .routes.auth import auth
    from .routes.vehicle import vehicle
    from .routes.tracking import tracking
    from .routes.admin import admin
    from .routes.trip import trip

    app.register_blueprint(auth)
    app.register_blueprint(vehicle)
    app.register_blueprint(tracking)
    app.register_blueprint(admin)
    app.register_blueprint(trip)

    # Health Check
    @app.route('/health')
    def health_check():
        try:
            db.session.execute(db.text('SELECT 1'))
            return {'status': 'healthy', 'database': 'connected'}, 200
        except Exception:
            return {'status': 'unhealthy', 'database': 'disconnected'}, 503

    # Error Handlers
    @app.errorhandler(403)
    def forbidden(e):
        return render_template('403.html'), 403

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(429)
    def ratelimit_handler(e):
        return render_template('429.html'), 429

    @app.errorhandler(500)
    def internal_server_error(e):
        app.logger.error(f"Server Error: {e}")
        return render_template('500.html'), 500

    return app
