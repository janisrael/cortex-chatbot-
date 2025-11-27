#!/usr/bin/env python3
"""Test RAG flow: Upload document, ingest, and test chatbot retrieval"""
import requests
import json
import time
import sys

BASE_URL = "http://127.0.0.1:6001"

# Test credentials (adjust if needed)
TEST_USERNAME = "testuser"
TEST_PASSWORD = "testpass123"

def login():
    """Login and get session"""
    session = requests.Session()
    login_data = {
        "username": TEST_USERNAME,
        "password": TEST_PASSWORD
    }
    response = session.post(f"{BASE_URL}/login", json=login_data, allow_redirects=False)
    
    if response.status_code == 200:
        print("✅ Login successful")
        return session
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(f"Response: {response.text}")
        return None

def upload_file(session, file_path):
    """Upload a file"""
    print(f"\n📤 Uploading file: {file_path}")
    
    with open(file_path, 'rb') as f:
        files = {'file': (file_path.split('/')[-1], f, 'text/plain')}
        data = {'category': 'general'}  # Default category
        
        response = session.post(f"{BASE_URL}/api/files", files=files, data=data)
    
    if response.status_code == 200:
        result = response.json()
        file_id = result.get('file_id')
        print(f"✅ File uploaded successfully. File ID: {file_id}")
        return file_id
    else:
        print(f"❌ Upload failed: {response.status_code}")
        print(f"Response: {response.text}")
        return None

def ingest_file(session, file_id):
    """Ingest a file into the knowledge base"""
    print(f"\n🔍 Ingesting file ID: {file_id}")
    
    response = session.post(f"{BASE_URL}/api/files/{file_id}/ingest", json={})
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ File ingested successfully")
        print(f"   Message: {result.get('message', 'N/A')}")
        return True
    else:
        print(f"❌ Ingestion failed: {response.status_code}")
        print(f"Response: {response.text}")
        return False

def test_chatbot(session, question):
    """Test chatbot with a question"""
    print(f"\n💬 Testing chatbot with question: '{question}'")
    
    response = session.post(
        f"{BASE_URL}/api/chat",
        json={"message": question},
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        result = response.json()
        answer = result.get('response', 'No response')
        print(f"✅ Chatbot responded:")
        print(f"   Answer: {answer[:200]}...")
        return answer
    else:
        print(f"❌ Chat request failed: {response.status_code}")
        print(f"Response: {response.text}")
        return None

def main():
    """Main test flow"""
    print("=" * 60)
    print("RAG Flow Test")
    print("=" * 60)
    
    # Step 1: Login
    session = login()
    if not session:
        print("\n❌ Cannot proceed without login")
        sys.exit(1)
    
    # Step 2: Upload file
    file_path = "test_rag_document.txt"
    file_id = upload_file(session, file_path)
    if not file_id:
        print("\n❌ Cannot proceed without file upload")
        sys.exit(1)
    
    # Step 3: Wait a moment
    print("\n⏳ Waiting 2 seconds before ingestion...")
    time.sleep(2)
    
    # Step 4: Ingest file
    if not ingest_file(session, file_id):
        print("\n❌ Cannot proceed without ingestion")
        sys.exit(1)
    
    # Step 5: Wait for ingestion to complete
    print("\n⏳ Waiting 3 seconds for ingestion to complete...")
    time.sleep(3)
    
    # Step 6: Test chatbot with specific questions
    test_questions = [
        "What is the CEO's name?",
        "What is the company's phone number?",
        "Where is the headquarters located?",
        "What is the pricing for monthly subscription?",
        "What is the email for support?"
    ]
    
    print("\n" + "=" * 60)
    print("Testing RAG Retrieval")
    print("=" * 60)
    
    for question in test_questions:
        answer = test_chatbot(session, question)
        if answer:
            # Check if answer contains expected information
            print(f"   ✓ Got response")
        print()
        time.sleep(1)  # Small delay between requests
    
    print("=" * 60)
    print("Test Complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()

