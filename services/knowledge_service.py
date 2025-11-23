"""Knowledge base and vectorstore service"""
import os
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings


# Global embeddings - initialized in app.py
embeddings = None

# Export embeddings for use in other modules
__all__ = ['embeddings', 'set_embeddings', 'get_user_vectorstore', 'get_knowledge_stats', 'remove_file_from_vectorstore']


def set_embeddings(embeddings_instance):
    """Set the global embeddings instance"""
    global embeddings
    embeddings = embeddings_instance


def get_user_knowledge_base_path(user_id):
    """Get the knowledge base path for a specific user"""
    return f"./chroma_db/user_{user_id}"


def get_user_vectorstore(user_id):
    """Get or create vectorstore for specific user"""
    global embeddings
    if not embeddings:
        print("❌ Embeddings not available for vectorstore - trying to initialize...")
        # Try to initialize embeddings if not set
        try:
            from langchain_community.embeddings import HuggingFaceEmbeddings
            embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
            set_embeddings(embeddings)
            print("✅ Embeddings initialized on-demand")
        except Exception as e:
            print(f"❌ Failed to initialize embeddings: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    kb_path = get_user_knowledge_base_path(user_id)
    print(f"📁 Creating vectorstore for user {user_id} at: {kb_path}")
    
    # Create directory if it doesn't exist
    os.makedirs(kb_path, exist_ok=True)
    
    try:
        # Create/load vectorstore for this user
        print(f"🔧 Initializing Chroma vectorstore...")
        user_vectorstore = Chroma(
            persist_directory=kb_path,
            embedding_function=embeddings
        )
        print(f"✅ Chroma vectorstore object created")
        
        # Always return the vectorstore - Chroma will create collection on first use
        # Even if empty, it can still be used for chat (just won't have RAG context)
        return user_vectorstore
            
    except Exception as e:
        print(f"❌ Error creating vectorstore for user {user_id}: {e}")
        import traceback
        traceback.print_exc()
        return None


def remove_file_from_vectorstore(user_id, filename):
    """Remove all chunks related to a specific file from user's vectorstore"""
    try:
        user_vectorstore = get_user_vectorstore(user_id)
        if not user_vectorstore:
            print(f"⚠️ Vectorstore not available for user {user_id}")
            return False
        
        collection = user_vectorstore._collection
        
        # Delete documents by metadata filter
        try:
            # Get all documents with this source file
            results = collection.get(
                where={"source_file": filename}
            )
            
            if results and 'ids' in results and len(results['ids']) > 0:
                # Delete the documents
                collection.delete(ids=results['ids'])
                print(f"✅ Deleted {len(results['ids'])} chunks from vectorstore for file: {filename}")
                return True
            else:
                print(f"ℹ️ No chunks found in vectorstore for file: {filename}")
                return True  # File not in vectorstore is okay
                
        except Exception as e:
            print(f"⚠️ Error removing file from vectorstore (may not be in vectorstore): {e}")
            # Don't fail if file isn't in vectorstore
            return True
            
    except Exception as e:
        print(f"❌ Error removing file from vectorstore: {e}")
        import traceback
        traceback.print_exc()
        return False


def get_knowledge_stats(user_id):
    """Get knowledge base statistics for a user"""
    try:
        user_vectorstore = get_user_vectorstore(user_id)
        doc_count = 0
        db_status = "unknown"
        
        if user_vectorstore:
            try:
                # Try to get document count
                retriever = user_vectorstore.as_retriever(search_kwargs={"k": 10000})
                test_docs = retriever.get_relevant_documents("")
                doc_count = len(test_docs) if test_docs else 0
                db_status = "active"
            except Exception as e:
                print(f"⚠️ Error checking vectorstore: {e}")
                db_status = "error"
        
        # Get file count
        from services.file_service import list_user_files
        files = list_user_files(user_id)
        
        return {
            "total_documents": max(0, doc_count),
            "vector_store_status": db_status,
            "uploaded_files": files
        }
    except Exception as e:
        print(f"❌ Stats error: {e}")
        return {
            "total_documents": 0,
            "vector_store_status": "error",
            "uploaded_files": []
        }

