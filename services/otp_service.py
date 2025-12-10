"""
OTP Service for generating, sending, and verifying OTP codes
"""
from models.otp import OTP
from utils.email_utils import send_otp_email


class OTPService:
    """Service for OTP operations"""
    
    # Rate limiting: max 5 OTPs per hour per email (more lenient)
    MAX_OTPS_PER_HOUR = 5
    # Rate limiting: max 3 OTPs per 15 minutes (short-term protection)
    MAX_OTPS_PER_15MIN = 3
    
    @staticmethod
    def generate_and_send_otp(email, purpose='registration', user_id=None):
        """
        Generate OTP and send via email
        
        Args:
            email: Email address
            purpose: Purpose of OTP
            user_id: Optional user ID
            
        Returns:
            tuple: (success: bool, otp_code: str or None, error_message: str or None)
        """
        try:
            from datetime import datetime, timedelta
            
            # Short-term rate limiting (15 minutes) - more strict
            recent_count_15min = OTP.get_recent_otp_count(email, purpose, minutes=15)
            if recent_count_15min >= OTPService.MAX_OTPS_PER_15MIN:
                oldest_time = OTP.get_oldest_recent_otp_time(email, purpose, minutes=15)
                if oldest_time:
                    if isinstance(oldest_time, str):
                        oldest_time = datetime.fromisoformat(oldest_time.replace('Z', '+00:00'))
                    wait_until = oldest_time + timedelta(minutes=15)
                    wait_minutes = int((wait_until - datetime.now()).total_seconds() / 60)
                    if wait_minutes > 0:
                        return False, None, f"Too many OTP requests. Please wait {wait_minutes} minute(s) before requesting another."
                return False, None, "Too many OTP requests. Please wait 15 minutes before requesting another."
            
            # Long-term rate limiting (1 hour) - more lenient
            recent_count_hour = OTP.get_recent_otp_count(email, purpose, minutes=60)
            if recent_count_hour >= OTPService.MAX_OTPS_PER_HOUR:
                oldest_time = OTP.get_oldest_recent_otp_time(email, purpose, minutes=60)
                if oldest_time:
                    if isinstance(oldest_time, str):
                        oldest_time = datetime.fromisoformat(oldest_time.replace('Z', '+00:00'))
                    wait_until = oldest_time + timedelta(minutes=60)
                    wait_minutes = int((wait_until - datetime.now()).total_seconds() / 60)
                    if wait_minutes > 0:
                        return False, None, f"Rate limit reached. Please wait {wait_minutes} minute(s) before requesting another OTP."
                return False, None, "Rate limit reached. Please wait 1 hour before requesting another OTP."
            
            # Generate OTP
            otp_code = OTP.create_otp(email, purpose, user_id)
            if not otp_code:
                return False, None, "Failed to generate OTP"
            
            # Send OTP email
            email_sent, error_msg = send_otp_email(email, otp_code, purpose)
            if not email_sent:
                return False, None, error_msg or "Failed to send OTP email"
            
            return True, otp_code, None
            
        except Exception as e:
            print(f"❌ Error in generate_and_send_otp: {e}")
            import traceback
            traceback.print_exc()
            return False, None, str(e)
    
    @staticmethod
    def verify_otp_code(email, otp_code, purpose='registration'):
        """
        Verify OTP code
        
        Args:
            email: Email address
            otp_code: OTP code to verify
            purpose: Purpose of OTP
            
        Returns:
            tuple: (success: bool, message: str, otp_id: int or None)
        """
        return OTP.verify_otp(email, otp_code, purpose)
    
    @staticmethod
    def resend_otp(email, purpose='registration', user_id=None):
        """
        Resend OTP to email
        
        Args:
            email: Email address
            purpose: Purpose of OTP
            user_id: Optional user ID
            
        Returns:
            tuple: (success: bool, message: str)
        """
        return OTPService.generate_and_send_otp(email, purpose, user_id)
    
    @staticmethod
    def cleanup_expired_otps():
        """Clean up expired OTPs"""
        return OTP.cleanup_expired()

