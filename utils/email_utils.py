"""Email utility functions for sending feedback and notifications"""
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime


def get_smtp_config():
    """Get SMTP configuration from environment variables"""
    # Try SMTP_USERNAME first (preferred), then fallback to SMTP_USER
    smtp_user = os.getenv('SMTP_USERNAME', '') or os.getenv('SMTP_USER', '')
    smtp_password = os.getenv('SMTP_PASSWORD', '')
    
    # Debug logging (only in development)
    if os.getenv('FLASK_ENV') == 'development':
        print(f"🔍 SMTP Config Debug:")
        print(f"   SMTP_SERVER: {os.getenv('SMTP_SERVER', 'smtp.gmail.com')}")
        print(f"   SMTP_PORT: {os.getenv('SMTP_PORT', '587')}")
        print(f"   SMTP_USERNAME: {'Set' if os.getenv('SMTP_USERNAME') else 'Not set'}")
        print(f"   SMTP_USER: {'Set' if os.getenv('SMTP_USER') else 'Not set'}")
        print(f"   SMTP_PASSWORD: {'Set' if smtp_password else 'Not set'}")
        print(f"   Final user: {'Set' if smtp_user else 'Missing'}")
    
    return {
        'server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
        'port': int(os.getenv('SMTP_PORT', '587')),
        'user': smtp_user,
        'password': smtp_password
    }


def send_otp_email(email, otp_code, purpose='registration'):
    """
    Send OTP verification email
    
    Args:
        email: Recipient email address
        otp_code: 6-digit OTP code
        purpose: Purpose of OTP (registration, forgot_password, etc.)
    
    Returns:
        tuple: (success: bool, error_message: str or None)
    """
    try:
        smtp_config = get_smtp_config()
        
        # Validate SMTP configuration
        if not smtp_config['user'] or not smtp_config['password']:
            error_msg = "SMTP credentials not configured"
            print(f"⚠️ {error_msg}")
            print(f"   SMTP_USERNAME env var: {'Set' if os.getenv('SMTP_USERNAME') else 'Not set'}")
            print(f"   SMTP_USER env var: {'Set' if os.getenv('SMTP_USER') else 'Not set'}")
            print(f"   SMTP_PASSWORD env var: {'Set' if os.getenv('SMTP_PASSWORD') else 'Not set'}")
            print(f"   Final config user: {'Set' if smtp_config['user'] else 'Missing'}")
            print(f"   Final config password: {'Set' if smtp_config['password'] else 'Missing'}")
            return False, error_msg
        
        # Create email message
        msg = MIMEMultipart()
        msg['From'] = smtp_config['user']
        msg['To'] = email
        msg['Subject'] = "Cortex AI - Email Verification Code"
        
        # Format email body
        purpose_text = {
            'registration': 'complete your registration',
            'email_verification': 'verify your email address',
            'forgot_password': 'reset your password',
            'email_change': 'verify your new email address',
            'two_factor_auth': 'complete two-factor authentication'
        }.get(purpose, 'verify your account')
        
        body = f"""
Hello,

Your verification code for Cortex AI is:

    {otp_code}

This code will expire in 15 minutes.

Please use this code to {purpose_text}.

If you didn't request this code, please ignore this email.

---
Cortex AI Team
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        print(f"📧 Sending OTP email to {email}...")
        server = smtplib.SMTP(smtp_config['server'], smtp_config['port'])
        server.starttls()
        server.login(smtp_config['user'], smtp_config['password'])
        server.sendmail(smtp_config['user'], email, msg.as_string())
        server.quit()
        
        print(f"✅ OTP email sent successfully to {email}")
        return True, None
        
    except smtplib.SMTPAuthenticationError as e:
        error_msg = f"SMTP Authentication Error: {e}"
        print(f"❌ {error_msg}")
        import traceback
        traceback.print_exc()
        return False, error_msg
    except smtplib.SMTPException as e:
        error_msg = f"SMTP Error: {e}"
        print(f"❌ {error_msg}")
        import traceback
        traceback.print_exc()
        return False, error_msg
    except Exception as e:
        error_msg = f"Error sending OTP email: {e}"
        print(f"❌ {error_msg}")
        import traceback
        traceback.print_exc()
        return False, error_msg


def send_feedback_email(feedback_type, subject, message, username, user_email):
    """
    Send feedback email to the configured recipient
    
    Args:
        feedback_type: Type of feedback (bug, feature, opinion, other)
        subject: Feedback subject line
        message: Feedback message content
        username: Username of the person submitting feedback
        user_email: Email of the person submitting feedback
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        smtp_config = get_smtp_config()
        
        # Validate SMTP configuration
        if not smtp_config['user'] or not smtp_config['password']:
            error_msg = "⚠️ SMTP credentials not configured. Please set SMTP_USER and SMTP_PASSWORD in .env"
            print(error_msg)
            print(f"   SMTP_USER: {'Set' if smtp_config['user'] else 'Missing'}")
            print(f"   SMTP_PASSWORD: {'Set' if smtp_config['password'] else 'Missing'}")
            return False
        
        # Create email message
        msg = MIMEMultipart()
        msg['From'] = smtp_config['user']
        msg['To'] = smtp_config['user']  # Send to self
        msg['Subject'] = f"[Cortex AI Feedback] {feedback_type.upper()}: {subject}"
        
        # Format email body
        body = f"""
New Feedback Submission from Cortex AI

Type: {feedback_type.upper()}
Subject: {subject}
User: {username}
Email: {user_email or 'Not provided'}

Message:
{message}

---
Submitted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        print(f"📧 Attempting to send feedback email...")
        print(f"   SMTP Server: {smtp_config['server']}:{smtp_config['port']}")
        print(f"   From: {smtp_config['user']}")
        print(f"   To: {smtp_config['user']}")
        
        server = smtplib.SMTP(smtp_config['server'], smtp_config['port'])
        server.starttls()
        server.login(smtp_config['user'], smtp_config['password'])
        server.sendmail(smtp_config['user'], smtp_config['user'], msg.as_string())
        server.quit()
        
        print(f"✅ Feedback email sent successfully: {feedback_type} from {username}")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        error_msg = f"⚠️ SMTP Authentication failed: {e}"
        print(error_msg)
        print("   Check if SMTP_USER and SMTP_PASSWORD are correct")
        print("   For Gmail, you may need to use an App Password instead of your regular password")
        import traceback
        traceback.print_exc()
        return False
    except smtplib.SMTPException as e:
        error_msg = f"⚠️ SMTP Error: {e}"
        print(error_msg)
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        error_msg = f"⚠️ Error sending feedback email: {e}"
        print(error_msg)
        import traceback
        traceback.print_exc()
        return False

