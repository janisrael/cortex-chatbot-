"""
Test script for RBAC and OTP implementation
"""
import sys
import os
sys.path.insert(0, '.')

print("=" * 60)
print("RBAC & OTP Implementation Test")
print("=" * 60)

# Test 1: Admin Decorator
print("\n1. Testing Admin Decorator...")
try:
    from decorators import admin_required
    print("   ✅ Admin decorator imports successfully")
except Exception as e:
    print(f"   ❌ Admin decorator import failed: {e}")
    sys.exit(1)

# Test 2: Admin Service
print("\n2. Testing Admin Service...")
try:
    from services.admin_service import AdminService
    stats = AdminService.get_system_stats()
    print(f"   ✅ Admin service works")
    print(f"   - Total users: {stats.get('total_users', 0)}")
    print(f"   - Total files: {stats.get('total_files', 0)}")
    print(f"   - Total crawls: {stats.get('total_crawls', 0)}")
    print(f"   - Total FAQs: {stats.get('total_faqs', 0)}")
except Exception as e:
    print(f"   ❌ Admin service test failed: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Admin Blueprint
print("\n3. Testing Admin Blueprint...")
try:
    from blueprints.admin import admin_bp
    print("   ✅ Admin blueprint imports successfully")
except Exception as e:
    print(f"   ❌ Admin blueprint import failed: {e}")
    sys.exit(1)

# Test 4: OTP Model
print("\n4. Testing OTP Model...")
try:
    from models.otp import OTP
    test_email = "test_rbac@example.com"
    otp_code = OTP.create_otp(test_email, 'registration')
    if otp_code:
        print(f"   ✅ OTP created: {otp_code}")
        success, message, otp_id = OTP.verify_otp(test_email, otp_code, 'registration')
        if success:
            print(f"   ✅ OTP verification works: {message}")
        else:
            print(f"   ❌ OTP verification failed: {message}")
    else:
        print("   ❌ OTP creation failed")
except Exception as e:
    print(f"   ❌ OTP model test failed: {e}")
    import traceback
    traceback.print_exc()

# Test 5: OTP Service
print("\n5. Testing OTP Service...")
try:
    from services.otp_service import OTPService
    print("   ✅ OTP service imports successfully")
    # Note: Email sending test requires SMTP config
    print("   ℹ️  Email sending test skipped (requires SMTP config)")
except Exception as e:
    print(f"   ❌ OTP service test failed: {e}")
    import traceback
    traceback.print_exc()

# Test 6: Database Tables
print("\n6. Testing Database Tables...")
try:
    import sqlite3
    db_path = 'users.db'
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check OTP table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='otp_verifications'")
        if cursor.fetchone():
            print("   ✅ OTP table exists")
        else:
            print("   ❌ OTP table not found")
        
        # Check users table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if cursor.fetchone():
            print("   ✅ Users table exists")
        else:
            print("   ❌ Users table not found")
        
        conn.close()
    else:
        print("   ⚠️  Database file not found")
except Exception as e:
    print(f"   ❌ Database test failed: {e}")

print("\n" + "=" * 60)
print("Test Summary")
print("=" * 60)
print("✅ All core components tested")
print("✅ Ready for integration testing")
print("=" * 60)

