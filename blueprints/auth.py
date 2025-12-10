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
            
            # Redirect admins to admin dashboard
            if user.is_admin():
                if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({"status": "success", "message": "Login successful", "redirect": "/admin/dashboard"})
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('admin.dashboard'))
            
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
        
        # Get JSON data (more reliable than request.json)
        # Try multiple methods to get JSON data
        json_data = {}
        try:
            if request.is_json:
                json_data = request.get_json(silent=True) or {}
            elif request.content_type and 'application/json' in request.content_type:
                json_data = request.get_json(silent=True) or {}
            else:
                # Try to parse JSON from raw data
                try:
                    import json
                    if request.data:
                        json_data = json.loads(request.data.decode('utf-8')) or {}
                except:
                    pass
        except Exception as e:
            print(f"DEBUG - Error getting JSON: {e}")
            json_data = {}
        
        print(f"DEBUG - json_data: {json_data}")
        print(f"DEBUG - json_data type: {type(json_data)}")
        print(f"DEBUG - json_data keys: {list(json_data.keys()) if isinstance(json_data, dict) else 'N/A'}")
        
        # Extract ALL possible fields from request (both JSON and form)
        # This ensures variables are defined even if OTP check fails
        email = json_data.get('email') or request.form.get('email')
        username = json_data.get('username') or request.form.get('username')
        password = json_data.get('password') or request.form.get('password')
        otp_code = json_data.get('otp_code') or request.form.get('otp_code')
        
        print(f"DEBUG - Extracted: email={email}, username={username}, password={'***' if password else None}, otp_code={otp_code}")
        print(f"DEBUG - OTP code check: otp_code={otp_code}, type={type(otp_code)}, truthy={bool(otp_code)}, stripped={str(otp_code).strip() if otp_code else None}")
        
        # Check if OTP code is provided (not None and not empty string)
        # Use explicit boolean check to ensure proper evaluation
        has_otp_code = otp_code is not None and str(otp_code).strip() != ''
        print(f"DEBUG - has_otp_code: {has_otp_code}")
        
        if has_otp_code:
            # This is OTP verification - verify OTP and create user
            from flask import session
            from services.otp_service import OTPService
            from flask_login import login_user
            
            # Get registration data from session
            reg_data = session.get('pending_registration')
            if not reg_data:
                if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({"status": "error", "message": "Registration session expired. Please start over."}), 400
                flash('Registration session expired. Please start over.', 'error')
                return render_template('auth/register.html', cache_busting_version='1.0.2')
            
            # Verify OTP
            success, message, otp_id = OTPService.verify_otp_code(reg_data['email'], otp_code, 'registration')
            
            if success:
                # OTP verified - create user account
                user_id, error_msg = User.create_user(reg_data['email'], reg_data['username'], reg_data['password'], role='user')
                
                if user_id:
                    # Login user
                    user = User.get_by_id(user_id)
                    if user:
                        login_user(user)
                        session.pop('pending_registration', None)
                        
                        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                            return jsonify({
                                "status": "success",
                                "message": "Registration successful! Welcome to Cortex AI.",
                                "redirect": url_for('dashboard.dashboard')
                            }), 200
                        flash('Registration successful! Welcome to Cortex AI.', 'success')
                        return redirect(url_for('dashboard.dashboard'))
                    else:
                        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                            return jsonify({"status": "error", "message": "Failed to create account. Please try again."}), 500
                        flash('Failed to create account. Please try again.', 'error')
                        session.pop('pending_registration', None)
                        return render_template('auth/register.html', cache_busting_version='1.0.2')
                else:
                    # User creation failed - show specific error message
                    error_message = error_msg or "Failed to create account. Please try again."
                    if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return jsonify({"status": "error", "message": error_message}), 400
                    flash(error_message, 'error')
                    session.pop('pending_registration', None)
                    return render_template('auth/register.html', cache_busting_version='1.0.2')
            else:
                # OTP verification failed
                if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({"status": "error", "message": message}), 400
                flash(message, 'error')
                return render_template('auth/register.html', cache_busting_version='1.0.2', show_otp=True, email=reg_data['email'])
        
        # Initial registration - validate and send OTP (don't create user yet)
        from flask import session
        from services.otp_service import OTPService
        
        # Validate username and email BEFORE sending OTP
        if User.get_by_email(email):
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    "status": "error",
                    "message": "An account with this email already exists. Please use a different email or log in."
                }), 400
            flash('An account with this email already exists. Please use a different email or log in.', 'error')
            return render_template('auth/register.html', cache_busting_version='1.0.2')
        
        if User.username_exists(username):
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    "status": "error",
                    "message": f"Username '{username}' is already taken. Please choose a different username."
                }), 400
            flash(f"Username '{username}' is already taken. Please choose a different username.", 'error')
            return render_template('auth/register.html', cache_busting_version='1.0.2')
        
        # Store registration data in session (temporarily)
        session['pending_registration'] = {
            'email': email,
            'username': username,
            'password': password
        }
        
        # Generate and send OTP (without user_id since user doesn't exist yet)
        success, otp_code, error_msg = OTPService.generate_and_send_otp(
            email, 
            purpose='registration',
            user_id=None  # User not created yet
        )
        
        if not success:
            session.pop('pending_registration', None)
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    "status": "error",
                    "message": error_msg or "Failed to send verification code. Please try again."
                }), 500
            flash(error_msg or "Failed to send verification code. Please try again.", 'error')
            return render_template('auth/register.html', cache_busting_version='1.0.2')
        
        # OTP sent successfully - return success with OTP form flag
        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                "status": "otp_sent",
                "message": "Verification code sent to your email. Please enter the code below.",
                "email": email,
                "requires_verification": True
            }), 200
        # For form submission, show OTP form on same page
        flash('Verification code sent to your email. Please enter the code below.', 'info')
        return render_template('auth/register.html', cache_busting_version='1.0.2', show_otp=True, email=email)
        
        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({"status": "error", "message": "Registration failed. Please try again."}), 500
        flash('Registration failed. Please try again.', 'error')
        return render_template('auth/register.html', cache_busting_version='1.0.2')
    
    # GET request - show register page
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.dashboard'))
    
    return render_template('auth/register.html', cache_busting_version='1.0.2')


@auth_bp.route("/verify-otp", methods=["GET", "POST"])
def verify_otp():
    """OTP verification page - handles both registration and password reset"""
    from flask import session
    from services.otp_service import OTPService
    
    if request.method == 'POST':
        # Get JSON data (more reliable than request.json)
        json_data = request.get_json(silent=True) or {}
        
        # Extract fields from JSON or form
        email = json_data.get('email') or request.form.get('email')
        otp_code = json_data.get('otp_code') or request.form.get('otp_code')
        purpose = json_data.get('purpose', 'registration') or request.form.get('purpose', 'registration')
        
        print(f"DEBUG verify-otp - email={email}, otp_code={otp_code}, purpose={purpose}")
        
        if not email or not otp_code:
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({"status": "error", "message": "Email and OTP code are required"}), 400
            flash('Email and OTP code are required', 'error')
            return render_template('auth/verify_otp.html', email=email or session.get('pending_verification_email'))
        
        # Verify OTP
        success, message, otp_id = OTPService.verify_otp_code(email, otp_code, purpose)
        
        if success:
            # Check if this is registration flow (user doesn't exist yet)
            if purpose == 'registration':
                # Get registration data from session
                reg_data = session.get('pending_registration')
                if not reg_data:
                    if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return jsonify({"status": "error", "message": "Registration session expired. Please start over."}), 400
                    flash('Registration session expired. Please start over.', 'error')
                    return redirect(url_for('auth.register'))
                
                # OTP verified - create user account
                user_id, error_msg = User.create_user(reg_data['email'], reg_data['username'], reg_data['password'], role='user')
                
                if user_id:
                    # Login user
                    user = User.get_by_id(user_id)
                    if user:
                        login_user(user)
                        session.pop('pending_registration', None)
                        
                        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                            return jsonify({
                                "status": "success",
                                "message": "Registration successful! Please log in to continue.",
                                "redirect": url_for('auth.login')
                            }), 200
                        flash('Registration successful! Please log in to continue.', 'success')
                        return redirect(url_for('auth.login'))
                    else:
                        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                            return jsonify({"status": "error", "message": "Failed to create account. Please try again."}), 500
                        flash('Failed to create account. Please try again.', 'error')
                        session.pop('pending_registration', None)
                        return redirect(url_for('auth.register'))
                else:
                    # User creation failed - show specific error message
                    error_message = error_msg or "Failed to create account. Please try again."
                    if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return jsonify({"status": "error", "message": error_message}), 400
                    flash(error_message, 'error')
                    session.pop('pending_registration', None)
                    return redirect(url_for('auth.register'))
            else:
                # Other purposes (password reset, etc.) - user should already exist
                user = User.get_by_email(email)
                if user:
                    login_user(user)
                    session.pop('pending_verification_email', None)
                    
                    if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return jsonify({
                            "status": "success",
                            "message": "Email verified successfully!",
                            "redirect": url_for('dashboard.dashboard')
                        }), 200
                    flash('Email verified successfully!', 'success')
                    return redirect(url_for('dashboard.dashboard'))
                else:
                    if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return jsonify({"status": "error", "message": "User not found"}), 404
                    flash('User not found', 'error')
                    return redirect(url_for('auth.register'))
        else:
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({"status": "error", "message": message}), 400
            flash(message, 'error')
            return render_template('auth/verify_otp.html', email=email)
    
    # GET request - show verification page
    email = session.get('pending_verification_email')
    if not email:
        flash('No pending verification. Please register first.', 'info')
        return redirect(url_for('auth.register'))
    
    return render_template('auth/verify_otp.html', email=email)


@auth_bp.route("/resend-otp", methods=["POST"])
def resend_otp():
    """Resend OTP code"""
    from flask import session
    from services.otp_service import OTPService
    
    email = request.form.get('email') or (request.json.get('email') if request.is_json else None)
    purpose = request.form.get('purpose', 'registration') or (request.json.get('purpose', 'registration') if request.is_json else 'registration')
    
    if not email:
        # Get email from pending registration session
        reg_data = session.get('pending_registration')
        if reg_data:
            email = reg_data.get('email')
    
    if not email:
        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({"status": "error", "message": "Email is required"}), 400
        flash('Email is required', 'error')
        return redirect(url_for('auth.register'))
    
    # For registration, user doesn't exist yet
    user_id = None
    if purpose == 'registration':
        reg_data = session.get('pending_registration')
        if not reg_data:
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({"status": "error", "message": "Registration session expired. Please start over."}), 400
            flash('Registration session expired. Please start over.', 'error')
            return redirect(url_for('auth.register'))
    else:
        # For other purposes, get user_id if user exists
        user = User.get_by_email(email)
        user_id = user.id if user else None
    
    # Resend OTP
    success, otp_code, error_msg = OTPService.resend_otp(email, purpose, user_id)
    
    if success:
        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                "status": "success",
                "message": "Verification code resent to your email"
            }), 200
        flash('Verification code resent to your email', 'success')
        return render_template('auth/register.html', cache_busting_version='1.0.2', show_otp=True, email=email)
    else:
        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({"status": "error", "message": error_msg or "Failed to resend OTP"}), 400
        flash(error_msg or "Failed to resend OTP", 'error')
        return render_template('auth/register.html', cache_busting_version='1.0.2', show_otp=True, email=email)


@auth_bp.route("/logout")
@login_required
def logout():
    """Logout user"""
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('auth.login'))

