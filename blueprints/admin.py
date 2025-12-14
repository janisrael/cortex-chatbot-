"""
Admin Blueprint for admin dashboard and user management
"""
from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from decorators import admin_required
from services.admin_service import AdminService
from models.api_key import AdminAPIKey

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


@admin_bp.route('/api/api-keys', methods=['GET'])
@login_required
@admin_required
def get_api_keys():
    """Get all admin API keys"""
    try:
        keys = AdminAPIKey.get_all()
        return jsonify({
            'success': True,
            'api_keys': keys
        }), 200
    except Exception as e:
        print(f"❌ Error getting API keys: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Failed to fetch API keys'
        }), 500


@admin_bp.route('/api/api-keys', methods=['POST'])
@login_required
@admin_required
def create_api_key():
    """Create a new admin API key"""
    try:
        data = request.json
        name = data.get('name', 'Untitled Key')
        key_type = data.get('key_type', 'custom')
        
        if key_type not in ['default', 'fallback', 'custom']:
            return jsonify({
                'success': False,
                'error': 'Invalid key_type. Must be default, fallback, or custom'
            }), 400
        
        result = AdminAPIKey.create(
            name=name,
            key_type=key_type,
            created_by=current_user.id
        )
        
        if result:
            return jsonify({
                'success': True,
                'api_key': {
                    'id': result['id'],
                    'name': result['name'],
                    'key_type': result['key_type'],
                    'token': result['token']  # Only returned on creation
                }
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to create API key'
            }), 500
    except Exception as e:
        print(f"❌ Error creating API key: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Failed to create API key'
        }), 500


@admin_bp.route('/api/api-keys/<int:key_id>', methods=['PUT'])
@login_required
@admin_required
def update_api_key(key_id):
    """Update an admin API key"""
    try:
        data = request.json
        name = data.get('name')
        is_active = data.get('is_active')
        
        if name is None and is_active is None:
            return jsonify({
                'success': False,
                'error': 'No fields to update'
            }), 400
        
        success = AdminAPIKey.update(
            id=key_id,
            name=name,
            is_active=is_active
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': 'API key updated successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to update API key'
            }), 500
    except Exception as e:
        print(f"❌ Error updating API key: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Failed to update API key'
        }), 500


@admin_bp.route('/api/api-keys/<int:key_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_api_key(key_id):
    """Delete an admin API key"""
    try:
        success = AdminAPIKey.delete(key_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'API key deleted successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to delete API key'
            }), 500
    except Exception as e:
        print(f"❌ Error deleting API key: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Failed to delete API key'
        }), 500

