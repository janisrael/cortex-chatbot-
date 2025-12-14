#!/usr/bin/env python3
"""Clear test vectorstore for clean testing"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from app import app
from services.knowledge_service import get_user_vectorstore

TEST_USER_ID = 1

def clear_vectorstore():
    """Clear the test user's vectorstore"""
    print("="*80)
    print("CLEARING TEST VECTORSTORE")
    print("="*80)
    
    with app.app_context():
        vectorstore = get_user_vectorstore(TEST_USER_ID)
        if not vectorstore:
            print("❌ Vectorstore not found")
            return False
        
        try:
            # Get collection
            collection = vectorstore._collection
            
            # Get count before deletion
            count_before = collection.count()
            print(f"📊 Documents in vectorstore before: {count_before}")
            
            # Delete all documents
            # ChromaDB requires a where clause, so we'll delete by user_id
            result = collection.delete(
                where={"user_id": str(TEST_USER_ID)}
            )
            
            # Also try deleting without where clause (if supported)
            try:
                collection.delete()
            except:
                pass
            
            # Get count after deletion
            count_after = collection.count()
            print(f"📊 Documents in vectorstore after: {count_after}")
            print(f"✅ Deleted {count_before - count_after} documents")
            
            return True
        except Exception as e:
            print(f"❌ Error clearing vectorstore: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    success = clear_vectorstore()
    sys.exit(0 if success else 1)


