"""Knowledge base and vectorstore service"""
import os
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings


# Global embeddings - initialized in app.py
embeddings = None
_last_vectorstore_error = None


def get_last_vectorstore_error():
    return _last_vectorstore_error

# Export embeddings for use in other modules
__all__ = ['embeddings', 'set_embeddings', 'get_user_vectorstore', 'get_knowledge_stats', 'remove_file_from_vectorstore']


def set_embeddings(embeddings_instance):
    """Set the global embeddings instance"""
    global embeddings
    embeddings = embeddings_instance


def get_user_knowledge_base_path(user_id):
    """Get the knowledge base path for a specific user"""
    # Use absolute path to ensure it works regardless of working directory
    if os.getenv('CHROMA_DB_PATH'):
        chroma_base = os.environ['CHROMA_DB_PATH']
    elif os.getenv('FLASK_ENV', '').lower() == 'production':
        chroma_base = '/opt/cortex/chroma_db'
    else:
        chroma_base = os.path.join(os.getcwd(), 'chroma_db')
    return os.path.join(chroma_base, f"user_{user_id}")


def get_user_vectorstore(user_id):
    """Get or create vectorstore for specific user"""
    global embeddings, _last_vectorstore_error
    _last_vectorstore_error = None
    if not embeddings:
        print("❌ Embeddings not available for vectorstore - trying to initialize...")
        try:
            from utils.ml_cache import load_embeddings

            embeddings = load_embeddings()
            set_embeddings(embeddings)
            print("✅ Embeddings initialized on-demand")
        except Exception as e:
            _last_vectorstore_error = f"Embeddings init failed: {e}"
            print(f"❌ Failed to initialize embeddings: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    kb_path = get_user_knowledge_base_path(user_id)
    print(f"📁 Creating vectorstore for user {user_id} at: {kb_path}")
    
    # Create directory if it doesn't exist with proper permissions
    os.makedirs(kb_path, exist_ok=True)
    # Ensure directory is writable
    os.chmod(kb_path, 0o755)
    
    try:
        # Create/load vectorstore for this user
        print(f"🔧 Initializing Chroma vectorstore...")
        
        # Use collection_name to ensure user isolation
        collection_name = f"user_{user_id}_collection"
        
        # Use PersistentClient for embedded mode (not Client which expects server)
        import chromadb
        import shutil
        
        client = None
        
        # Step 1: Check if database exists and test if it's accessible
        if os.path.exists(kb_path):
            try:
                # Try to create client and test access
                test_client = chromadb.PersistentClient(path=kb_path)
                test_client.list_collections()  # Test if database is accessible
                client = test_client
                print(f"✅ Existing database is accessible")
            except Exception as test_error:
                # Database exists but is corrupted or inaccessible
                error_str = str(test_error)
                if "PanicException" in error_str or "panic" in error_str.lower() or "range" in error_str.lower() or "tenant" in error_str.lower():
                    print(f"⚠️ Database corrupted or inaccessible: {error_str[:150]}")
                    print(f"🔄 Deleting corrupted database...")
                    shutil.rmtree(kb_path, ignore_errors=True)
                    os.makedirs(kb_path, exist_ok=True)
                    client = None  # Will create fresh below
                else:
                    # Unknown error, try to reset anyway
                    print(f"⚠️ Database error: {error_str[:150]}")
                    print(f"🔄 Attempting to reset database...")
                    shutil.rmtree(kb_path, ignore_errors=True)
                    os.makedirs(kb_path, exist_ok=True)
                    client = None
        
        # Step 2: Create client (fresh database or existing good one)
        if not client:
            try:
                print(f"📦 Creating fresh PersistentClient...")
                client = chromadb.PersistentClient(path=kb_path)
                print(f"✅ PersistentClient created successfully")
            except Exception as client_error:
                error_str = str(client_error)
                print(f"⚠️ Failed to create PersistentClient: {error_str[:150]}")
                # Last resort: delete and try once more
                if os.path.exists(kb_path):
                    print(f"🔄 Last attempt: deleting and recreating...")
                    shutil.rmtree(kb_path, ignore_errors=True)
                    os.makedirs(kb_path, exist_ok=True)
                try:
                    client = chromadb.PersistentClient(path=kb_path)
                    print(f"✅ PersistentClient created after reset")
                except Exception as final_error:
                    _last_vectorstore_error = f"Chroma init failed: {final_error}"
                    print(f"❌ Failed to create PersistentClient even after reset: {final_error}")
                    import traceback
                    traceback.print_exc()
                    return None
        
        # Step 3: Create Chroma vectorstore (ALWAYS runs if client exists)
        if client:
            try:
                # Ensure all subdirectories and files are writable before creating vectorstore
                # Use more permissive permissions to avoid readonly database errors
                for root, dirs, files in os.walk(kb_path):
                    for d in dirs:
                        dir_path = os.path.join(root, d)
                        try:
                            os.chmod(dir_path, 0o777)
                        except:
                            pass
                    for f in files:
                        file_path = os.path.join(root, f)
                        try:
                            os.chmod(file_path, 0o666)
                        except:
                            pass
                
                user_vectorstore = Chroma(
                    client=client,
                    collection_name=collection_name,
                    embedding_function=embeddings
                )
                print(f"✅ Chroma vectorstore object created for collection: {collection_name}")
                
                # Verify vectorstore is actually usable before returning
                try:
                    # Test that we can access the collection
                    test_collection = user_vectorstore._collection
                    if test_collection is None:
                        print(f"⚠️ Warning: Collection is None after creation")
                        return None
                    # Try a simple operation to verify it works (but don't fail if it errors)
                    try:
                        _ = test_collection.count()
                    except:
                        pass  # Count might fail on empty collection, that's OK
                    print(f"✅ Vectorstore verified and ready")
                    return user_vectorstore
                except Exception as verify_error:
                    print(f"⚠️ Warning: Vectorstore verification error (but returning anyway): {verify_error}")
                    # Return it anyway - it might still work
                    return user_vectorstore
            except Exception as chroma_error:
                _last_vectorstore_error = f"Chroma vectorstore: {chroma_error}"
                print(f"❌ Error creating Chroma vectorstore: {chroma_error}")
                import traceback
                traceback.print_exc()
                return None
        else:
            _last_vectorstore_error = "Chroma client unavailable"
            print(f"❌ No client available to create vectorstore")
            return None
            
    except Exception as e:
        _last_vectorstore_error = str(e)
        print(f"❌ Error creating vectorstore for user {user_id}: {e}")
        import traceback
        traceback.print_exc()
        return None


def remove_file_from_vectorstore(user_id, filename):
    """Remove all chunks related to a specific file from user's vectorstore"""
    try:
        user_vectorstore = get_user_vectorstore(user_id)
        if user_vectorstore is None:
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
                # Method 1: Try to get count directly from ChromaDB collection (most reliable)
                if hasattr(user_vectorstore, '_collection'):
                    try:
                        collection = user_vectorstore._collection
                        # Get all document IDs to count
                        results = collection.get()
                        doc_count = len(results.get('ids', [])) if results and 'ids' in results else 0
                        db_status = "active"
                        print(f"✅ Got document count from collection: {doc_count}")
                    except Exception as coll_error:
                        print(f"⚠️ Error getting count from collection: {coll_error}")
                        # Fallback to retriever method
                        raise coll_error
                else:
                    # Method 2: Fallback to retriever method if collection not accessible
                    retriever = user_vectorstore.as_retriever(search_kwargs={"k": 10000})
                    # Use a generic query to retrieve all documents (k=10000 should get all)
                    # Use invoke() instead of get_relevant_documents() for LangChain 0.3.x
                    if hasattr(retriever, 'invoke'):
                        test_docs = retriever.invoke("document")
                    else:
                        # Fallback for older LangChain versions
                        test_docs = retriever.get_relevant_documents("document")
                    doc_count = len(test_docs) if test_docs else 0
                    db_status = "active"
                    print(f"✅ Got document count from retriever: {doc_count}")
            except Exception as e:
                print(f"⚠️ Error checking vectorstore: {e}")
                import traceback
                traceback.print_exc()
                db_status = "error"
                doc_count = 0
        
        # Get file count
        from services.file_service import list_user_files
        files = list_user_files(user_id)
        
        # Get FAQ count
        from models.faq import FAQ
        faqs = FAQ.get_all_by_user(user_id, status=None)  # Get all non-deleted FAQs
        ingested_faqs = [f for f in faqs if f.get('ingested_at')]
        
        return {
            "total_documents": max(0, doc_count),
            "vector_store_status": db_status,
            "uploaded_files": files,
            "faq_count": len(faqs),
            "ingested_faq_count": len(ingested_faqs)
        }
    except Exception as e:
        print(f"❌ Stats error: {e}")
        return {
            "total_documents": 0,
            "vector_store_status": "error",
            "uploaded_files": []
        }

