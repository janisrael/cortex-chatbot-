"""
OTP Service for generating, sending, and verifying OTP codes
"""
from models.otp import OTP
from utils.email_utils import send_otp_email


class OTPService:
    """Service for OTP operations"""
    
    # Rate limiting: max 3 OTPs per hour per email
    MAX_OTPS_PER_HOUR = 3
    
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
            # Rate limiting check
            recent_count = OTP.get_recent_otp_count(email, purpose, minutes=60)
            if recent_count >= OTPService.MAX_OTPS_PER_HOUR:
                return False, None, "Too many OTP requests. Please wait before requesting another."
            
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

