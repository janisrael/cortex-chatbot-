#!/usr/bin/env python3
"""
Comprehensive functionality tests for the chatbot
Tests: Registration, Login, User Isolation, Chat, Configuration
"""
import requests
import json
import time
import sys
from getpass import getpass

BASE_URL = "http://localhost:6001"
SESSION = requests.Session()

def print_test(name):
    print(f"\n{'='*60}")
    print(f"🧪 TEST: {name}")
    print(f"{'='*60}")

def print_success(msg):
    print(f"✅ {msg}")

def print_error(msg):
    print(f"❌ {msg}")

def print_info(msg):
    print(f"ℹ️  {msg}")

def test_registration():
    """Test user registration"""
    print_test("User Registration")
    
    # Generate unique email
    import random
    test_email = f"testuser_{random.randint(1000, 9999)}@test.com"
    test_username = f"testuser_{random.randint(1000, 9999)}"
    
    data = {
        "username": test_username,
        "email": test_email,
        "password": "test123456",
        "confirm_password": "test123456"
    }
    
    try:
        response = SESSION.post(
            f"{BASE_URL}/register",
            headers={"X-Requested-With": "XMLHttpRequest"},
            data=data
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("status") == "success":
                print_success(f"Registration successful! User: {test_email}")
                return test_email, "test123456", test_username
            else:
                print_error(f"Registration failed: {result.get('message')}")
                return None, None, None
        else:
            print_error(f"Registration failed with status {response.status_code}")
            print_error(f"Response: {response.text[:200]}")
            return None, None, None
    except Exception as e:
        print_error(f"Registration error: {e}")
        return None, None, None

def test_login(email, password):
    """Test user login"""
    print_test("User Login")
    
    data = {
        "email": email,
        "password": password
    }
    
    try:
        response = SESSION.post(
            f"{BASE_URL}/login",
            headers={"X-Requested-With": "XMLHttpRequest"},
            data=data
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("status") == "success":
                print_success(f"Login successful! Redirect: {result.get('redirect')}")
                return True
            else:
                print_error(f"Login failed: {result.get('message')}")
                return False
        else:
            print_error(f"Login failed with status {response.status_code}")
            print_error(f"Response: {response.text[:200]}")
            return False
    except Exception as e:
        print_error(f"Login error: {e}")
        return False

def test_dashboard_access():
    """Test dashboard access after login"""
    print_test("Dashboard Access")
    
    try:
        response = SESSION.get(f"{BASE_URL}/dashboard")
        
        if response.status_code == 200:
            print_success("Dashboard accessible")
            return True
        elif response.status_code == 302:
            print_error("Dashboard redirected (not logged in)")
            return False
        else:
            print_error(f"Dashboard access failed with status {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Dashboard access error: {e}")
        return False

def test_chat_functionality():
    """Test chat with user-specific RAG"""
    print_test("Chat Functionality (User-Specific RAG)")
    
    test_message = "Hello, what can you help me with?"
    
    try:
        response = SESSION.post(
            f"{BASE_URL}/chat",
            json={"message": test_message},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            if "response" in result:
                reply = result["response"]
                print_success(f"Chat working! Response received: {reply[:100]}...")
                return True
            else:
                print_error(f"Chat response missing 'response' field: {result}")
                return False
        elif response.status_code == 401:
            print_error("Chat requires authentication (401)")
            return False
        else:
            print_error(f"Chat failed with status {response.status_code}")
            print_error(f"Response: {response.text[:200]}")
            return False
    except Exception as e:
        print_error(f"Chat error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_user_isolation():
    """Test that user has isolated data directories"""
    print_test("User Data Isolation")
    
    import os
    
    # Check if user directories exist (we'll check for user_2 as test)
    user_dirs = [
        "chroma_db/user_2",
        "uploads/user_2",
        "config/user_2",
        "data/user_2"
    ]
    
    all_exist = True
    for dir_path in user_dirs:
        if os.path.exists(dir_path):
            print_success(f"Directory exists: {dir_path}")
        else:
            print_error(f"Directory missing: {dir_path}")
            all_exist = False
    
    return all_exist

def test_openai_configuration():
    """Test OpenAI API configuration"""
    print_test("OpenAI API Configuration")
    
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    
    if api_key:
        print_success(f"OpenAI API key is set (length: {len(api_key)})")
        
        # Check if it starts with sk-
        if api_key.startswith("sk-"):
            print_success("API key format looks correct")
        else:
            print_error("API key format may be incorrect (should start with sk-)")
        
        return True
    else:
        print_error("OPENAI_API_KEY not found in environment")
        print_info("Check .env file or environment variables")
        return False

def test_configuration_endpoints():
    """Test configuration endpoints"""
    print_test("Configuration Endpoints")
    
    # Test getting current configuration
    try:
        response = SESSION.get(f"{BASE_URL}/api/website-config")
        
        if response.status_code == 200:
            config = response.json()
            print_success("Configuration endpoint accessible")
            print_info(f"Bot name: {config.get('botName', 'N/A')}")
            print_info(f"Website ID: {config.get('websiteId', 'N/A')}")
            print_info(f"Primary color: {config.get('primaryColor', 'N/A')}")
            return True
        else:
            print_error(f"Configuration endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Configuration test error: {e}")
        return False

def test_file_upload():
    """Test file upload functionality"""
    print_test("File Upload (User-Specific)")
    
    # Create a test file
    test_file_content = "This is a test document for the chatbot knowledge base."
    test_filename = "test_document.txt"
    
    try:
        files = {"file": (test_filename, test_file_content, "text/plain")}
        data = {"category": "company_details"}
        
        response = SESSION.post(
            f"{BASE_URL}/api/upload",
            files=files,
            data=data
        )
        
        if response.status_code == 200:
            result = response.json()
            print_success(f"File upload successful: {result.get('message', 'OK')}")
            return True
        else:
            print_error(f"File upload failed: {response.status_code}")
            print_error(f"Response: {response.text[:200]}")
            return False
    except Exception as e:
        print_error(f"File upload error: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🚀 COMPREHENSIVE FUNCTIONALITY TESTS")
    print("="*60)
    
    # Check if server is running
    print_info("Checking if server is running...")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=2)
        print_success("Server is running")
    except:
        print_error(f"Server not running at {BASE_URL}")
        print_info("Please start the server first: python3 app.py")
        sys.exit(1)
    
    results = {}
    
    # Test 1: OpenAI Configuration
    results["openai_config"] = test_openai_configuration()
    
    # Test 2: Registration
    email, password, username = test_registration()
    results["registration"] = email is not None
    
    if not results["registration"]:
        print_error("\n❌ Registration failed - cannot continue tests")
        print_summary(results)
        sys.exit(1)
    
    # Test 3: Login
    results["login"] = test_login(email, password)
    
    if not results["login"]:
        print_error("\n❌ Login failed - cannot continue tests")
        print_summary(results)
        sys.exit(1)
    
    # Test 4: Dashboard Access
    results["dashboard"] = test_dashboard_access()
    
    # Test 5: User Isolation
    results["isolation"] = test_user_isolation()
    
    # Test 6: Chat Functionality
    results["chat"] = test_chat_functionality()
    
    # Test 7: Configuration Endpoints
    results["configuration"] = test_configuration_endpoints()
    
    # Test 8: File Upload
    results["file_upload"] = test_file_upload()
    
    # Print summary
    print_summary(results)
    
    # Exit with appropriate code
    if all(results.values()):
        print("\n✅ ALL TESTS PASSED!")
        sys.exit(0)
    else:
        print("\n❌ SOME TESTS FAILED")
        sys.exit(1)

def print_summary(results):
    """Print test summary"""
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name.replace('_', ' ').title()}")
    
    passed = sum(results.values())
    total = len(results)
    print(f"\nTotal: {passed}/{total} tests passed")

if __name__ == "__main__":
    main()

