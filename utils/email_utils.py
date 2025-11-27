"""Email utility functions for sending feedback and notifications"""
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime


def get_smtp_config():
    """Get SMTP configuration from environment variables"""
    return {
        'server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
        'port': int(os.getenv('SMTP_PORT', '587')),
        'user': os.getenv('SMTP_USER', ''),
        'password': os.getenv('SMTP_PASSWORD', '')
    }


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
            print("⚠️ SMTP credentials not configured. Please set SMTP_USER and SMTP_PASSWORD in .env")
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
        server = smtplib.SMTP(smtp_config['server'], smtp_config['port'])
        server.starttls()
        server.login(smtp_config['user'], smtp_config['password'])
        server.sendmail(smtp_config['user'], smtp_config['user'], msg.as_string())
        server.quit()
        
        print(f"✅ Feedback email sent: {feedback_type} from {username}")
        return True
        
    except Exception as e:
        print(f"⚠️ Error sending feedback email: {e}")
        import traceback
        traceback.print_exc()
        return False

