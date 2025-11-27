#!/usr/bin/env python3
"""Test email sending functionality"""
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.email_utils import send_feedback_email, get_smtp_config

def test_smtp_config():
    """Test SMTP configuration"""
    print("=" * 60)
    print("Testing SMTP Configuration")
    print("=" * 60)
    
    config = get_smtp_config()
    print(f"SMTP Server: {config['server']}")
    print(f"SMTP Port: {config['port']}")
    print(f"SMTP User: {config['user'][:10] + '...' if len(config['user']) > 10 else config['user']}")
    print(f"SMTP Password: {'Set' if config['password'] else 'Not Set'}")
    
    if not config['user'] or not config['password']:
        print("\n❌ SMTP credentials not configured!")
        print("   Please set SMTP_USER and SMTP_PASSWORD in .env file")
        return False
    
    print("\n✅ SMTP configuration looks good")
    return True

def test_email_sending():
    """Test sending a feedback email"""
    print("\n" + "=" * 60)
    print("Testing Email Sending")
    print("=" * 60)
    
    # Test data
    feedback_type = "test"
    subject = "Test Feedback Submission"
    message = "This is a test email to verify the feedback email system is working correctly."
    username = "Test User"
    user_email = "test@example.com"
    
    print(f"\nSending test email...")
    print(f"  Type: {feedback_type}")
    print(f"  Subject: {subject}")
    print(f"  From: {username} ({user_email})")
    
    try:
        result = send_feedback_email(feedback_type, subject, message, username, user_email)
        
        if result:
            print("\n✅ Email sent successfully!")
            print("   Check your inbox for the test email.")
            return True
        else:
            print("\n❌ Email sending failed!")
            print("   Check the error messages above for details.")
            return False
    except Exception as e:
        print(f"\n❌ Exception during email sending: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("\n" + "=" * 60)
    print("Email Sending Test")
    print("=" * 60)
    
    # Test 1: Check SMTP configuration
    if not test_smtp_config():
        print("\n❌ Cannot proceed - SMTP not configured")
        sys.exit(1)
    
    # Test 2: Send test email
    if test_email_sending():
        print("\n" + "=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)
        sys.exit(0)
    else:
        print("\n" + "=" * 60)
        print("❌ Email sending test failed")
        print("=" * 60)
        sys.exit(1)

if __name__ == "__main__":
    main()

