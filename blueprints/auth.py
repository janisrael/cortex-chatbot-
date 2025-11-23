"""Authentication blueprint - login, register, logout"""
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from models import User

auth_bp = Blueprint('auth', __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Login page and authentication"""
    if request.method == 'POST':
        # Debug: Print what we're receiving
        print(f"DEBUG LOGIN - request.form: {dict(request.form)}")
        print(f"DEBUG LOGIN - request.is_json: {request.is_json}")
        print(f"DEBUG LOGIN - Content-Type: {request.content_type}")
        if request.is_json:
            print(f"DEBUG LOGIN - request.json: {request.json}")
        
        email = request.form.get('email') or (request.json.get('email') if request.is_json else None)
        password = request.form.get('password') or (request.json.get('password') if request.is_json else None)
        
        print(f"DEBUG LOGIN - Extracted values: email={email}, password={'***' if password else None}")
        
        if not email or not password:
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({"status": "error", "message": "Email and password are required"}), 400
            flash('Email and password are required', 'error')
            return render_template('auth/login.html', cache_busting_version='1.0.2')
        
        user = User.get_by_email(email)
        
        if user and user.check_password(password):
            login_user(user, remember=True)
            User.update_last_login(user.id)
            
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({"status": "success", "message": "Login successful", "redirect": "/dashboard"})
            
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard.dashboard'))
        else:
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({"status": "error", "message": "Invalid email or password"}), 401
            flash('Invalid email or password', 'error')
            return render_template('auth/login.html', cache_busting_version='1.0.2')
    
    # GET request - show login page
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.dashboard'))
    
    return render_template('auth/login.html', cache_busting_version='1.0.2')


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """Registration page"""
    if request.method == 'POST':
        # Debug: Print what we're receiving
        print(f"DEBUG - request.form: {dict(request.form)}")
        print(f"DEBUG - request.is_json: {request.is_json}")
        print(f"DEBUG - Content-Type: {request.content_type}")
        if request.is_json:
            print(f"DEBUG - request.json: {request.json}")
        
        email = request.form.get('email') or (request.json.get('email') if request.is_json else None)
        username = request.form.get('username') or (request.json.get('username') if request.is_json else None)
        password = request.form.get('password') or (request.json.get('password') if request.is_json else None)
        
        print(f"DEBUG - Extracted values: email={email}, username={username}, password={'***' if password else None}")
        
        if not all([email, username, password]):
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({"status": "error", "message": "Email, username, and password are required"}), 400
            flash('All fields are required', 'error')
            return render_template('auth/register.html', cache_busting_version='1.0.2')
        
        if User.email_exists(email):
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({"status": "error", "message": "Email already registered"}), 400
            flash('Email already registered', 'error')
            return render_template('auth/register.html', cache_busting_version='1.0.2')
        
        if User.username_exists(username):
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({"status": "error", "message": "Username already taken"}), 400
            flash('Username already taken', 'error')
            return render_template('auth/register.html', cache_busting_version='1.0.2')
        
        user_id = User.create_user(email, username, password, role='user')
        
        if user_id:
            # v1 behavior: Do NOT auto-login, redirect to login page
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    "status": "success",
                    "message": "Registration successful. Please log in.",
                    "redirect": url_for('auth.login')
                })
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('auth.login'))
        
        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({"status": "error", "message": "Registration failed. Please try again."}), 500
        flash('Registration failed. Please try again.', 'error')
        return render_template('auth/register.html', cache_busting_version='1.0.2')
    
    # GET request - show register page
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.dashboard'))
    
    return render_template('auth/register.html', cache_busting_version='1.0.2')


@auth_bp.route("/logout")
@login_required
def logout():
    """Logout user"""
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('auth.login'))

