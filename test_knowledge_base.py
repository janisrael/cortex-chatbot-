#!/usr/bin/env python3
"""
Test Knowledge Base Integration
Tests: Upload document, verify chatbot uses knowledge base
"""
import requests
import json
import os
import sys
import time

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

def test_login():
    """Login with test account"""
    print_test("Login")
    
    # Try to login with existing test account or create one
    test_email = "testuser_kb@test.com"
    test_password = "test123456"
    
    # Try registration first
    try:
        reg_data = {
            "username": "testuser_kb",
            "email": test_email,
            "password": test_password,
            "confirm_password": test_password
        }
        response = SESSION.post(
            f"{BASE_URL}/register",
            headers={"X-Requested-With": "XMLHttpRequest"},
            data=reg_data
        )
        if response.status_code == 200:
            result = response.json()
            if result.get("status") == "success":
                print_success("Registered new test account")
            else:
                print_info("Account may already exist")
    except:
        pass
    
    # Login
    data = {"email": test_email, "password": test_password}
    try:
        response = SESSION.post(
            f"{BASE_URL}/login",
            headers={"X-Requested-With": "XMLHttpRequest"},
            data=data
        )
        if response.status_code == 200:
            result = response.json()
            if result.get("status") == "success":
                print_success("Login successful")
                return True
    except Exception as e:
        print_error(f"Login failed: {e}")
    
    return False

def create_test_document():
    """Create a test document with specific information"""
    print_test("Creating Test Document")
    
    test_content = """Company Information Document

Our company, TechSolutions Inc., was founded in 2020.
We specialize in AI-powered software solutions.

Key Services:
1. Custom AI Chatbot Development
2. Machine Learning Model Training
3. Natural Language Processing Solutions
4. Data Analytics and Insights

Contact Information:
- Email: contact@techsolutions.com
- Phone: +1-555-0123
- Address: 123 Tech Street, San Francisco, CA 94105

Pricing:
- Basic Plan: $99/month
- Professional Plan: $299/month
- Enterprise Plan: Custom pricing

Our team consists of 25 experienced developers and data scientists.
We have completed over 150 projects for clients worldwide.

Special Offer: New customers get 20% off their first month.
"""
    
    test_file = "/tmp/test_company_info.txt"
    with open(test_file, 'w') as f:
        f.write(test_content)
    
    print_success(f"Created test document: {test_file}")
    print_info("Document contains: Company info, services, contact details, pricing")
    return test_file

def upload_document(filepath):
    """Upload the test document"""
    print_test("Uploading Document to Knowledge Base")
    
    try:
        with open(filepath, 'rb') as f:
            files = {'file': ('test_company_info.txt', f, 'text/plain')}
            data = {'category': 'company_details'}
            
            response = SESSION.post(
                f"{BASE_URL}/api/upload",
                files=files,
                data=data
            )
        
        if response.status_code == 200:
            result = response.json()
            print_success(f"File uploaded: {result.get('message')}")
            print_info(f"Category: {result.get('category')}")
            print_info(f"Filename: {result.get('filename')}")
            return True
        else:
            print_error(f"Upload failed: {response.status_code}")
            print_error(f"Response: {response.text[:200]}")
            return False
    except Exception as e:
        print_error(f"Upload error: {e}")
        import traceback
        traceback.print_exc()
        return False

def wait_for_processing():
    """Wait a moment for document processing"""
    print_info("Waiting for document processing...")
    time.sleep(3)

def test_chat_with_knowledge_base():
    """Test chat with questions that should use the knowledge base"""
    print_test("Testing Chatbot with Knowledge Base")
    
    test_questions = [
        {
            "question": "What services does TechSolutions Inc. offer?",
            "expected_keywords": ["AI Chatbot", "Machine Learning", "NLP", "Data Analytics"]
        },
        {
            "question": "What is the contact email for TechSolutions?",
            "expected_keywords": ["contact@techsolutions.com"]
        },
        {
            "question": "What are the pricing plans?",
            "expected_keywords": ["$99", "$299", "Basic", "Professional", "Enterprise"]
        },
        {
            "question": "How many employees does the company have?",
            "expected_keywords": ["25", "developers", "data scientists"]
        },
        {
            "question": "What is the special offer for new customers?",
            "expected_keywords": ["20%", "first month", "discount"]
        }
    ]
    
    results = []
    
    for i, test in enumerate(test_questions, 1):
        print(f"\n📝 Question {i}: {test['question']}")
        
        try:
            response = SESSION.post(
                f"{BASE_URL}/chat",
                json={"message": test['question']},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                reply = result.get("response", "")
                
                # Check if response contains expected keywords
                found_keywords = []
                missing_keywords = []
                
                for keyword in test['expected_keywords']:
                    if keyword.lower() in reply.lower():
                        found_keywords.append(keyword)
                    else:
                        missing_keywords.append(keyword)
                
                print(f"📤 Response: {reply[:200]}...")
                print(f"✅ Found keywords: {found_keywords}")
                
                if missing_keywords:
                    print(f"⚠️  Missing keywords: {missing_keywords}")
                
                # Calculate score
                score = len(found_keywords) / len(test['expected_keywords']) * 100
                results.append({
                    "question": test['question'],
                    "score": score,
                    "found": found_keywords,
                    "missing": missing_keywords
                })
                
                if score >= 50:
                    print_success(f"Knowledge base used! ({score:.0f}% match)")
                else:
                    print_error(f"Knowledge base may not be used ({score:.0f}% match)")
            else:
                print_error(f"Chat failed: {response.status_code}")
                print_error(f"Response: {response.text[:200]}")
                results.append({
                    "question": test['question'],
                    "score": 0,
                    "error": True
                })
        except Exception as e:
            print_error(f"Chat error: {e}")
            results.append({
                "question": test['question'],
                "score": 0,
                "error": True
            })
    
    return results

def test_list_files():
    """Verify file is in the list"""
    print_test("Verifying File in List")
    
    try:
        response = SESSION.get(f"{BASE_URL}/api/files")
        
        if response.status_code == 200:
            result = response.json()
            files = result.get("files", [])
            
            print_info(f"Total files: {result.get('total', 0)}")
            
            test_file = None
            for file in files:
                if file.get("filename") == "test_company_info.txt":
                    test_file = file
                    break
            
            if test_file:
                print_success("Test file found in file list")
                print_info(f"Category: {test_file.get('category')}")
                print_info(f"Size: {test_file.get('size')} bytes")
                return True
            else:
                print_error("Test file not found in list")
                return False
        else:
            print_error(f"Failed to list files: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"List files error: {e}")
        return False

def test_delete_file():
    """Test file deletion"""
    print_test("Testing File Deletion")
    
    try:
        response = SESSION.delete(
            f"{BASE_URL}/api/files/test_company_info.txt?category=company_details"
        )
        
        if response.status_code == 200:
            result = response.json()
            print_success(f"File deleted: {result.get('message')}")
            return True
        else:
            print_error(f"Delete failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Delete error: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🚀 KNOWLEDGE BASE INTEGRATION TEST")
    print("="*60)
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/", timeout=2)
        print_success("Server is running")
    except:
        print_error(f"Server not running at {BASE_URL}")
        print_info("Please start the server first: python3 app.py")
        sys.exit(1)
    
    # Test 1: Login
    if not test_login():
        print_error("Cannot continue without login")
        sys.exit(1)
    
    # Test 2: Create test document
    test_file = create_test_document()
    
    # Test 3: Upload document
    if not upload_document(test_file):
        print_error("Cannot continue without uploaded document")
        sys.exit(1)
    
    # Test 4: Wait for processing
    wait_for_processing()
    
    # Test 5: Verify file in list
    test_list_files()
    
    # Test 6: Test chat with knowledge base
    results = test_chat_with_knowledge_base()
    
    # Test 7: Delete file (cleanup)
    test_delete_file()
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    total_score = 0
    for result in results:
        if not result.get("error"):
            score = result["score"]
            total_score += score
            status = "✅" if score >= 50 else "⚠️"
            print(f"{status} {result['question'][:50]}... ({score:.0f}%)")
        else:
            print(f"❌ {result['question'][:50]}... (ERROR)")
    
    avg_score = total_score / len(results) if results else 0
    print(f"\n📈 Average Knowledge Base Usage: {avg_score:.1f}%")
    
    if avg_score >= 70:
        print_success("✅ Knowledge base is working well!")
    elif avg_score >= 50:
        print_info("⚠️  Knowledge base is partially working")
    else:
        print_error("❌ Knowledge base may not be working correctly")
    
    # Cleanup
    if os.path.exists(test_file):
        os.remove(test_file)
        print_info(f"Cleaned up test file: {test_file}")

if __name__ == "__main__":
    main()

