from flask import Blueprint, render_template, abort
from flask_login import login_required, current_user
from app.services.admin_service import AdminService

admin = Blueprint('admin', __name__)

@admin.route('/admin')
@login_required
def dashboard():
    """
    Admin system dashboard.
    """
    if current_user.role != 'admin':
        abort(403)

    result = AdminService.get_dashboard_stats()
    
    if not result["success"]:
        # Log error in production and show a user-friendly message
        abort(500)

    return render_template('admin_dashboard.html', **result["data"])
