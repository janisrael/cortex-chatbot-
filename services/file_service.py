"""File upload and management service"""
import os
from datetime import datetime
from werkzeug.utils import secure_filename
from utils.helpers import allowed_file
from langchain_community.document_loaders import PyPDFLoader, TextLoader, CSVLoader, Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter


def save_uploaded_file(user_id, file, category):
    """Save uploaded file to user's directory"""
    filename = secure_filename(file.filename)
    user_upload_dir = f"uploads/user_{user_id}"
    category_dir = os.path.join(user_upload_dir, category)
    os.makedirs(category_dir, exist_ok=True)
    
    filepath = os.path.join(category_dir, filename)
    file.save(filepath)
    return filepath, filename


def list_user_files(user_id):
    """List all files for a user"""
    user_upload_dir = f"uploads/user_{user_id}"
    files = []
    
    if os.path.exists(user_upload_dir):
        for category in os.listdir(user_upload_dir):
            category_path = os.path.join(user_upload_dir, category)
            if os.path.isdir(category_path):
                for filename in os.listdir(category_path):
                    filepath = os.path.join(category_path, filename)
                    if os.path.isfile(filepath):
                        file_stat = os.stat(filepath)
                        files.append({
                            "filename": filename,
                            "category": category,
                            "size": file_stat.st_size,
                            "uploaded_at": datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
                            "path": filepath
                        })
    
    return files


def delete_user_file(user_id, filename, category):
    """Delete a file from user's directory"""
    user_upload_dir = f"uploads/user_{user_id}"
    category_dir = os.path.join(user_upload_dir, category)
    filepath = os.path.join(category_dir, filename)
    
    if os.path.exists(filepath):
        os.remove(filepath)
        return True
    return False


def extract_text_from_file(filepath, filename):
    """Extract text from file for preview (does not ingest)"""
    try:
        file_ext = filename.lower().split('.')[-1]
        print(f"📄 Extracting text from {file_ext} file: {filename}")
        
        # Load document based on file extension
        try:
            if file_ext == 'pdf':
                # Try multiple PDF extraction methods for better accuracy
                full_text = None
                extraction_method = None
                
                # Method 1: Try pdfplumber (most accurate for text extraction)
                try:
                    import pdfplumber
                    full_text = ""
                    with pdfplumber.open(filepath) as pdf:
                        print(f"📚 pdfplumber: Found {len(pdf.pages)} pages")
                        for page_num, page in enumerate(pdf.pages):
                            page_text = page.extract_text()
                            if page_text:
                                full_text += f"\n\n--- Page {page_num + 1} ---\n\n{page_text}"
                    if full_text and len(full_text.strip()) > 50:
                        extraction_method = "pdfplumber"
                        print(f"✅ Extracted {len(full_text)} characters using pdfplumber")
                        return full_text.strip()
                except ImportError:
                    print("⚠️ pdfplumber not available, trying other methods...")
                except Exception as e:
                    print(f"⚠️ pdfplumber extraction failed: {e}")
                
                # Method 2: Try pypdf directly (more robust than PyPDFLoader)
                try:
                    import pypdf
                    full_text = ""
                    with open(filepath, 'rb') as file:
                        pdf_reader = pypdf.PdfReader(file)
                        print(f"📚 pypdf: Found {len(pdf_reader.pages)} pages")
                        for page_num, page in enumerate(pdf_reader.pages):
                            page_text = page.extract_text()
                            if page_text and page_text.strip():
                                full_text += f"\n\n--- Page {page_num + 1} ---\n\n{page_text}"
                    if full_text and len(full_text.strip()) > 50:
                        extraction_method = "pypdf"
                        print(f"✅ Extracted {len(full_text)} characters using pypdf")
                        return full_text.strip()
                except ImportError:
                    print("⚠️ pypdf not available, trying PyPDFLoader...")
                except Exception as e:
                    print(f"⚠️ pypdf extraction failed: {e}")
                
                # Method 3: Try PyPDFLoader (LangChain wrapper)
                try:
                    loader = PyPDFLoader(filepath)
                    documents = loader.load()
                    print(f"📚 PyPDFLoader: Loaded {len(documents)} pages from {filename}")
                    full_text = "\n\n".join([doc.page_content for doc in documents if doc.page_content and doc.page_content.strip()])
                    if full_text and len(full_text.strip()) > 50:
                        extraction_method = "PyPDFLoader"
                        print(f"✅ Extracted {len(full_text)} characters using PyPDFLoader")
                        return full_text
                except Exception as e:
                    print(f"⚠️ PyPDFLoader failed: {e}")
                
                # Method 4: Try PyPDF2 as fallback
                try:
                    import PyPDF2
                    full_text = ""
                    with open(filepath, 'rb') as file:
                        pdf_reader = PyPDF2.PdfReader(file)
                        print(f"📚 PyPDF2: Found {len(pdf_reader.pages)} pages")
                        for page_num, page in enumerate(pdf_reader.pages):
                            page_text = page.extract_text()
                            if page_text and page_text.strip():
                                full_text += f"\n\n--- Page {page_num + 1} ---\n\n{page_text}"
                    if full_text and len(full_text.strip()) > 50:
                        extraction_method = "PyPDF2"
                        print(f"✅ Extracted {len(full_text)} characters using PyPDF2")
                        return full_text.strip()
                except ImportError:
                    print("⚠️ PyPDF2 not available, skipping...")
                except Exception as e:
                    print(f"⚠️ PyPDF2 extraction failed: {e}")
                
                # If all methods failed or returned minimal text
                if not full_text or len(full_text.strip()) < 50:
                    print(f"⚠️ All PDF extraction methods failed or returned minimal text ({len(full_text) if full_text else 0} chars). File might be image-based (scanned PDF) or have complex formatting.")
                    warning_msg = "⚠️ Could not extract substantial text from PDF. This might be:\n- A scanned/image-based PDF (requires OCR)\n- A PDF with complex formatting\n- A password-protected PDF\n\nExtracted text (if any):\n" + (full_text[:500] if full_text else "None")
                    return warning_msg
                
                return full_text.strip()
                
            elif file_ext == 'csv':
                loader = CSVLoader(filepath)
                documents = loader.load()
                print(f"📚 Loaded {len(documents)} rows from CSV")
                full_text = "\n\n".join([doc.page_content for doc in documents])
                return full_text
            elif file_ext == 'docx':
                try:
                    loader = Docx2txtLoader(filepath)
                    documents = loader.load()
                    print(f"📚 Loaded {len(documents)} sections from DOCX")
                    full_text = "\n\n".join([doc.page_content for doc in documents])
                    return full_text
                except Exception as e:
                    print(f"⚠️ Could not load .docx file, trying as text: {e}")
                    loader = TextLoader(filepath, encoding='utf-8')
                    documents = loader.load()
                    full_text = "\n\n".join([doc.page_content for doc in documents])
                    return full_text
            elif file_ext == 'doc':
                # .doc files (older Microsoft Word format) require special handling
                # Try python-docx2txt first, then fallback methods
                try:
                    # Method 1: Try textract (if available) - handles both .doc and .docx
                    try:
                        import textract
                        full_text = textract.process(filepath).decode('utf-8')
                        if full_text and len(full_text.strip()) > 50:
                            print(f"✅ Extracted {len(full_text)} characters from .doc using textract")
                            return full_text.strip()
                    except ImportError:
                        print("⚠️ textract not available, trying other methods...")
                    except Exception as e:
                        print(f"⚠️ textract extraction failed: {e}")
                    
                    # Method 2: Try antiword (if available) - Linux command-line tool
                    try:
                        import subprocess
                        result = subprocess.run(['antiword', filepath], capture_output=True, text=True, timeout=30)
                        if result.returncode == 0 and result.stdout and len(result.stdout.strip()) > 50:
                            print(f"✅ Extracted {len(result.stdout)} characters from .doc using antiword")
                            return result.stdout.strip()
                    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
                        print(f"⚠️ antiword not available or timed out: {e}")
                    
                    # Method 3: Try catdoc (if available) - Linux command-line tool
                    try:
                        import subprocess
                        result = subprocess.run(['catdoc', filepath], capture_output=True, text=True, timeout=30)
                        if result.returncode == 0 and result.stdout and len(result.stdout.strip()) > 50:
                            print(f"✅ Extracted {len(result.stdout)} characters from .doc using catdoc")
                            return result.stdout.strip()
                    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
                        print(f"⚠️ catdoc not available or timed out: {e}")
                    
                    # Method 4: Last resort - warn user
                    print(f"⚠️ .doc file format not fully supported. Please convert to .docx or .txt")
                    return "⚠️ .doc file format (older Microsoft Word) is not fully supported. Please convert this file to .docx or .txt format for better compatibility."
                    
                except Exception as e:
                    print(f"❌ Error processing .doc file: {e}")
                    return f"⚠️ Error processing .doc file: {str(e)}. Please convert to .docx or .txt format."
            else:
                loader = TextLoader(filepath, encoding='utf-8')
                documents = loader.load()
                print(f"📚 Loaded {len(documents)} documents from text file")
                full_text = "\n\n".join([doc.page_content for doc in documents])
                return full_text
            
        except Exception as e:
            print(f"❌ Error loading file {filename}: {e}")
            import traceback
            traceback.print_exc()
            return None
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"❌ Text extraction error: {e}")
        print(f"Full traceback:\n{error_details}")
        return None


def process_file_for_user(filepath, filename, category, user_id):
    """Process file for specific user's knowledge base"""
    try:
        from services.knowledge_service import get_user_vectorstore, embeddings
        
        if not embeddings:
            print("❌ Embeddings not available")
            return False
        
        # Load document based on file extension
        file_ext = filename.lower().split('.')[-1]
        print(f"📄 Processing {file_ext} file: {filename}")
        
        try:
            if file_ext == 'pdf':
                loader = PyPDFLoader(filepath)
            elif file_ext == 'csv':
                loader = CSVLoader(filepath)
            elif file_ext == 'docx':
                try:
                    loader = Docx2txtLoader(filepath)
                except Exception as e:
                    print(f"⚠️ Could not load .docx file, trying as text: {e}")
                    loader = TextLoader(filepath, encoding='utf-8')
            elif file_ext == 'doc':
                # .doc files need special handling - use text extraction methods
                # For ingestion, we'll extract text first, then create a document
                try:
                    import textract
                    full_text = textract.process(filepath).decode('utf-8')
                    if not full_text or len(full_text.strip()) < 50:
                        raise Exception("textract returned insufficient text")
                    # Create a single document from extracted text
                    from langchain_core.documents import Document
                    documents = [Document(page_content=full_text.strip())]
                    print(f"✅ Extracted text from .doc file using textract")
                except ImportError:
                    # Fallback: try antiword or catdoc
                    try:
                        import subprocess
                        result = subprocess.run(['antiword', filepath], capture_output=True, text=True, timeout=30)
                        if result.returncode == 0 and result.stdout:
                            from langchain_core.documents import Document
                            documents = [Document(page_content=result.stdout.strip())]
                            print(f"✅ Extracted text from .doc file using antiword")
                        else:
                            raise Exception("antiword failed")
                    except:
                        try:
                            import subprocess
                            result = subprocess.run(['catdoc', filepath], capture_output=True, text=True, timeout=30)
                            if result.returncode == 0 and result.stdout:
                                from langchain_core.documents import Document
                                documents = [Document(page_content=result.stdout.strip())]
                                print(f"✅ Extracted text from .doc file using catdoc")
                            else:
                                raise Exception("catdoc failed")
                        except:
                            print(f"⚠️ .doc file not supported - please convert to .docx")
                            return False
                except Exception as e:
                    print(f"❌ Error processing .doc file: {e}")
                    return False
            else:
                loader = TextLoader(filepath, encoding='utf-8')
            
            documents = loader.load()
            print(f"📚 Loaded {len(documents)} documents from {filename}")
        except Exception as e:
            print(f"❌ Error loading file {filename}: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # Split into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        chunks = text_splitter.split_documents(documents)
        print(f"✂️ Split into {len(chunks)} chunks")
        
        # Add user-specific metadata
        for chunk in chunks:
            chunk.metadata.update({
                'source_file': filename,
                'upload_time': datetime.now().isoformat(),
                'category': category,
                'user_id': str(user_id)
            })
        
        # Add to user-specific vectorstore
        try:
            user_vectorstore = get_user_vectorstore(user_id)
            if user_vectorstore is None:
                print("❌ Failed to create/get user vectorstore")
                return False
            
            # Add documents to vectorstore
            print(f"📤 Adding {len(chunks)} chunks to vectorstore...")
            user_vectorstore.add_documents(chunks)
            print(f"✅ Added {len(chunks)} chunks from {filename} to user {user_id} knowledge base")
            
            return True
        except Exception as e:
            print(f"❌ Error adding to vectorstore: {e}")
            import traceback
            traceback.print_exc()
            return False
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"❌ File processing error for user {user_id}: {e}")
        print(f"Full traceback:\n{error_details}")
        return False

