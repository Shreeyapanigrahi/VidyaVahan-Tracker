import logging
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required
from app.forms import RegistrationForm, LoginForm
from app.services.auth_service import AuthService
from app import limiter
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def register():
    if current_user.is_authenticated:
        return redirect(url_for('vehicle.dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            AuthService.register_user(
                username=form.username.data,
                email=form.email.data,
                password=form.password.data
            )
            flash('Your account has been created! You are now able to log in', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            logger.exception("Registration failed for email %s", form.email.data)
            flash('Registration failed. Please try again.', 'danger')
    
    return render_template('register.html', title='Register', form=form)

@auth.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    if current_user.is_authenticated:
        return redirect(url_for('vehicle.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        try:
            user = AuthService.authenticate_user(
                email=form.email.data,
                password=form.password.data,
                remember=form.remember.data
            )
            if user:
                next_page = request.args.get('next')
                if next_page and urlparse(next_page).netloc == '':
                    return redirect(next_page)
                return redirect(url_for('vehicle.dashboard'))
            else:
                flash('Login Unsuccessful. Please check email and password', 'danger')
        except Exception as e:
            logger.exception("Login failed")
            flash('An error occurred during login. Please try again.', 'danger')
            
    return render_template('login.html', title='Login', form=form)

@auth.route('/logout')
@login_required
def logout():
    AuthService.logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/profile')
@login_required
def profile():
    from app.services.user_service import UserService
    stats = {}
    recent_activity = []
    active_trip = None
    
    try:
        stats = UserService.get_user_statistics(current_user.id)
        recent_activity = UserService.get_recent_activity(current_user.id)
        active_trip = UserService.get_active_trip(current_user.id)
    except Exception as e:
        logger.exception("Failed to load profile for user %s", current_user.id)
        # Fallback values are already initialized above
        
    return render_template('user_dashboard.html', 
                           stats=stats, 
                           recent_activity=recent_activity,
                           active_trip=active_trip)

