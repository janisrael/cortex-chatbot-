"""Blueprints package - register all blueprints"""
from flask import Flask
from .auth import auth_bp
from .dashboard import dashboard_bp
from .api import api_bp
from .widget import widget_bp
from .chat import chat_bp


def register_blueprints(app: Flask):
    """Register all blueprints with the Flask app"""
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(widget_bp)
    app.register_blueprint(chat_bp)

