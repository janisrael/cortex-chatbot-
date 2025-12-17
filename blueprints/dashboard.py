"""Dashboard blueprint"""
from flask import Blueprint, render_template, redirect, url_for, jsonify
from flask_login import login_required, current_user
from models import User

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route("/")
def index():
    """Root route - redirect to login or dashboard"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.dashboard'))
    return redirect(url_for('auth.login'))


@dashboard_bp.route("/landing")
def landing():
    """Landing page - public marketing page"""
    return render_template("landing.html")


@dashboard_bp.route("/dashboard")
@login_required
def dashboard():
    """Dashboard page - requires login"""
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    # Use dashboard/dashboard.html (tab-based design, will be modularized)
    return render_template("dashboard/dashboard.html", user=current_user)


@dashboard_bp.route("/chat-interface")
@login_required
def chat_interface():
    """Chat interface page"""
    from config.constants import SUGGESTED_MESSAGES
    return render_template("index.html", suggested=SUGGESTED_MESSAGES)


@dashboard_bp.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    try:
        return jsonify({
            "status": "healthy",
            "service": "chatbot-api",
            "version": "2.0"
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500


@dashboard_bp.route("/privacy-policy")
@login_required
def privacy_policy():
    """Privacy Policy page"""
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    return render_template("legal/privacy_policy.html", user=current_user)


@dashboard_bp.route("/terms-of-service")
@login_required
def terms_of_service():
    """Terms of Service page"""
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    return render_template("legal/terms_of_service.html", user=current_user)

