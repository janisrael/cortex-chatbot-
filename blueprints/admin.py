"""
Admin Blueprint for admin dashboard and user management
"""
from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from decorators import admin_required
from services.admin_service import AdminService

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Admin dashboard page"""
    return render_template('admin/dashboard.html')


@admin_bp.route('/api/users')
@login_required
@admin_required
def get_users():
    """Get all users with statistics (JSON API)"""
    try:
        users = AdminService.get_users_with_stats()
        return jsonify({
            'success': True,
            'users': users,
            'count': len(users)
        }), 200
    except Exception as e:
        print(f"❌ Error getting users: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Failed to fetch users'
        }), 500


@admin_bp.route('/api/stats')
@login_required
@admin_required
def get_stats():
    """Get system-wide statistics (JSON API)"""
    try:
        stats = AdminService.get_system_stats()
        return jsonify({
            'success': True,
            'stats': stats
        }), 200
    except Exception as e:
        print(f"❌ Error getting stats: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Failed to fetch statistics'
        }), 500


@admin_bp.route('/api/user/<int:user_id>/stats')
@login_required
@admin_required
def get_user_stats(user_id):
    """Get statistics for a specific user (JSON API)"""
    try:
        stats = AdminService.get_user_stats(user_id)
        return jsonify({
            'success': True,
            'stats': stats
        }), 200
    except Exception as e:
        print(f"❌ Error getting user stats: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Failed to fetch user statistics'
        }), 500

