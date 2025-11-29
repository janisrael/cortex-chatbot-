"""
Authorization decorators for role-based access control (RBAC)
"""
from functools import wraps
from flask import redirect, url_for, flash, jsonify, request
from flask_login import current_user


def admin_required(f):
    """
    Decorator to require admin role for accessing a route.
    
    Usage:
        @admin_bp.route('/admin/dashboard')
        @admin_required
        def admin_dashboard():
            return render_template('admin/dashboard.html')
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is authenticated
        if not current_user.is_authenticated:
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'error': 'Authentication required'}), 401
            flash('Please log in to access this page', 'error')
            return redirect(url_for('auth.login'))
        
        # Check if user is admin
        if not current_user.is_admin():
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'error': 'Admin access required'}), 403
            flash('Admin access required', 'error')
            return redirect(url_for('dashboard.dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function


def user_required(f):
    """
    Decorator to require user role (admin or regular user) for accessing a route.
    Viewers are not allowed.
    
    Usage:
        @bp.route('/some-route')
        @user_required
        def some_route():
            return render_template('some_template.html')
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is authenticated
        if not current_user.is_authenticated:
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'error': 'Authentication required'}), 401
            flash('Please log in to access this page', 'error')
            return redirect(url_for('auth.login'))
        
        # Check if user has user role (admin or user, not viewer)
        if not current_user.is_user():
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'error': 'User access required'}), 403
            flash('User access required', 'error')
            return redirect(url_for('dashboard.dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function

