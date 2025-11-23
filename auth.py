"""
Authentication and RBAC utilities
"""
from functools import wraps
from flask import abort, current_app
from flask_login import current_user


def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(401)
        if not current_user.is_admin():
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


def user_required(f):
    """Decorator to require user or admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(401)
        if not current_user.is_user():
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


def viewer_required(f):
    """Decorator to require any authenticated user (viewer, user, or admin)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(401)
        if not current_user.is_viewer():
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

