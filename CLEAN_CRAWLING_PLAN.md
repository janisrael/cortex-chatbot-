# 🕷️ Clean Web Crawling & Text Extraction Plan

**Version:** 2.0  
**Date:** 2025-11-23  
**Status:** Planning  
**Branch:** crawling-feature

---

## 🎯 Problem Statement

Current crawling implementation has issues:
- **Broken words** in extracted text
- **HTML artifacts** not properly removed
- **Encoding issues** causing garbled text
- **No preview** before saving to knowledge base
- **Poor text quality** affecting RAG performance
- **No tracking** of crawled URLs (separate from files)
- **No overview** of crawled websites

## 🎯 Requirements

1. **Separate table for crawled URLs** (like uploaded files)
2. **Overview display** showing crawled websites alongside uploaded files
3. **List format:** `URL | view | delete`
4. **Preview before ingesting** - user must verify text quality first
5. **User can edit** extracted text before saving
6. **User-isolated data** (same as uploaded documents)

---

## 🔍 Root Causes

1. **WebBaseLoader limitations:**
   - Basic HTML parsing
   - Doesn't handle JavaScript-rendered content well
   - No text cleaning/processing
   - Encoding issues

2. **No text cleaning:**
   - HTML tags not fully removed
   - Script/style content included
   - Whitespace issues
   - Special characters not handled

3. **No preview mechanism:**
   - Users can't see what will be saved
   - Can't verify quality before committing
   - No way to edit/clean before saving

4. **No tracking system:**
   - Crawled URLs not stored separately
   - No overview/list of crawled pages
   - Can't manage crawled content like files

---

## 💡 Solution: Clean Text Extraction with Preview

### Phase 1: Better Text Extraction Libraries

#### Option 1: Trafilatura (Recommended)
**Pros:**
- Excellent at extracting main content
- Removes navigation, ads, scripts automatically
- Handles encoding well
- Fast and lightweight
- Good for most websites

**Install:** `pip install trafilatura`

#### Option 2: Readability-lxml
**Pros:**
- Mozilla's readability algorithm
- Very good at extracting main content
- Removes boilerplate

**Install:** `pip install readability-lxml`

#### Option 3: html2text
**Pros:**
- Converts HTML to clean markdown/text
- Preserves structure
- Good for formatted content

**Install:** `pip install html2text`

#### Option 4: Selenium + BeautifulSoup (For JS-heavy sites)
**Pros:**
- Handles JavaScript-rendered content
- Can wait for dynamic content
- Full browser rendering

**Cons:**
- Heavy (requires browser)
- Slow
- Resource-intensive

**Recommendation:** Use **Trafilatura** as primary, with **html2text** as fallback.

---

## 🗄️ Database Schema

### `crawled_urls` Table
```sql
CREATE TABLE crawled_urls (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    url VARCHAR(500) NOT NULL,
    title VARCHAR(255),
    extracted_text TEXT,  -- Clean extracted text (not ingested yet)
    word_count INT DEFAULT 0,
    char_count INT DEFAULT 0,
    status ENUM('preview', 'ingested', 'deleted') DEFAULT 'preview',
    category VARCHAR(50) DEFAULT 'company_details',
    crawled_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    ingested_at DATETIME NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_url (url(255))
);
```

**Note:** 
- `extracted_text` stores the cleaned text (user can edit before ingesting)
- `status='preview'` means not yet ingested to vectorstore
- `status='ingested'` means saved to knowledge base
- User can view/edit/delete before ingesting

---

## 🛠️ Implementation Plan

### Step 1: Create Database Migration

**File:** `migrations.py`

Add migration 004:
```python
@staticmethod
def _migration_004_create_crawled_urls():
    """Create crawled_urls table"""
    # Implementation here
```

### Step 2: Create CrawledUrl Model

**File:** `models/crawled_url.py`

Similar to User model pattern (MySQL/SQLite support)

### Step 3: Create Text Cleaning Service

**File:** `services/text_cleaning_service.py`

```python
import re
import trafilatura
from html2text import HTML2Text
from bs4 import BeautifulSoup
import unicodedata

def clean_extracted_text(text):
    """Clean extracted text from web pages"""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove broken words (words split across lines)
    text = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', text)
    
    # Fix common encoding issues
    text = unicodedata.normalize('NFKD', text)
    
    # Remove special characters that shouldn't be there
    text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)\[\]\'\"\/]', '', text)
    
    # Fix multiple spaces
    text = re.sub(r' +', ' ', text)
    
    # Fix multiple newlines
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
    
    # Trim
    text = text.strip()
    
    return text

def extract_clean_text_from_url(url):
    """Extract clean text from URL using best available method"""
    try:
        # Try Trafilatura first (best for most sites)
        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            text = trafilatura.extract(downloaded)
            if text:
                return clean_extracted_text(text)
    except Exception as e:
        print(f"Trafilatura failed: {e}")
    
    try:
        # Fallback to html2text
        import requests
        response = requests.get(url, timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        response.raise_for_status()
        
        h = HTML2Text()
        h.ignore_links = False
        h.ignore_images = True
        h.body_width = 0  # Don't wrap
        text = h.handle(response.text)
        return clean_extracted_text(text)
    except Exception as e:
        print(f"html2text fallback failed: {e}")
        return None
```

### Step 2: Create Preview Endpoint (Saves to DB, not vectorstore)

**File:** `blueprints/api.py`

```python
@api_bp.route("/api/crawl-preview", methods=["POST"])
@login_required
def crawl_url_preview():
    """Crawl URL, extract clean text, save to crawled_urls table (preview status)"""
    try:
        data = request.json
        url = data.get('url')
        category = data.get('category', 'company_details')
        
        if not url:
            return jsonify({"error": "No URL provided"}), 400
        
        user_id = current_user.id
        
        # Check if URL already crawled
        from models.crawled_url import CrawledUrl
        existing = CrawledUrl.get_by_url(user_id, url)
        if existing and existing['status'] != 'deleted':
            return jsonify({
                "error": "URL already crawled",
                "crawled_id": existing['id'],
                "url": existing['url']
            }), 400
        
        # Extract clean text
        from services.text_cleaning_service import extract_clean_text_from_url
        
        text = extract_clean_text_from_url(url)
        
        if not text:
            return jsonify({"error": "Failed to extract content from URL"}), 400
        
        # Get text stats
        word_count = len(text.split())
        char_count = len(text)
        
        # Extract title from URL or text
        title = url.split('/')[-1] or url
        if len(text) > 100:
            # Try to get title from first line
            first_line = text.split('\n')[0][:100]
            if first_line:
                title = first_line
        
        # Save to crawled_urls table (status='preview')
        crawled_id = CrawledUrl.create(
            user_id=user_id,
            url=url,
            title=title,
            extracted_text=text,
            word_count=word_count,
            char_count=char_count,
            category=category,
            status='preview'
        )
        
        if not crawled_id:
            return jsonify({"error": "Failed to save crawled URL"}), 500
        
        return jsonify({
            "id": crawled_id,
            "url": url,
            "title": title,
            "preview": text[:2000],  # First 2000 chars for preview
            "full_text": text,  # Full text for editing
            "word_count": word_count,
            "char_count": char_count,
            "status": "preview",
            "message": "URL crawled successfully. Review the extracted text before ingesting."
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
```

### Step 3: Create List Endpoint

**File:** `blueprints/api.py`

```python
@api_bp.route("/api/crawled-urls", methods=["GET"])
@login_required
def list_crawled_urls():
    """List all crawled URLs for current user"""
    try:
        user_id = current_user.id
        from models.crawled_url import CrawledUrl
        
        urls = CrawledUrl.get_all_by_user(user_id)
        
        return jsonify({
            "urls": urls,
            "total": len(urls)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
```

### Step 4: Create View Endpoint

**File:** `blueprints/api.py`

```python
@api_bp.route("/api/crawled-urls/<int:crawled_id>", methods=["GET"])
@login_required
def view_crawled_url(crawled_id):
    """Get crawled URL details and extracted text"""
    try:
        user_id = current_user.id
        from models.crawled_url import CrawledUrl
        
        crawled = CrawledUrl.get_by_id(user_id, crawled_id)
        
        if not crawled:
            return jsonify({"error": "Crawled URL not found"}), 404
        
        return jsonify(crawled)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
```

### Step 5: Create Ingest Endpoint (Save to Vectorstore)

**File:** `blueprints/api.py`

```python
@api_bp.route("/api/crawled-urls/<int:crawled_id>/ingest", methods=["POST"])
@login_required
def ingest_crawled_url(crawled_id):
    """Ingest crawled URL to knowledge base (vectorstore)"""
    try:
        user_id = current_user.id
        data = request.json
        
        from models.crawled_url import CrawledUrl
        from services.knowledge_service import get_user_vectorstore, embeddings
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        from langchain.schema import Document
        from datetime import datetime
        
        # Get crawled URL
        crawled = CrawledUrl.get_by_id(user_id, crawled_id)
        if not crawled:
            return jsonify({"error": "Crawled URL not found"}), 404
        
        if crawled['status'] == 'ingested':
            return jsonify({"error": "URL already ingested"}), 400
        
        # Get text (user may have edited it)
        text = data.get('text', crawled['extracted_text'])
        if not text:
            return jsonify({"error": "No text to ingest"}), 400
        
        # Update text if edited
        if text != crawled['extracted_text']:
            CrawledUrl.update_text(crawled_id, text)
        
        # Split into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        
        doc = Document(
            page_content=text,
            metadata={
                'source_file': crawled['url'],
                'upload_time': datetime.now().isoformat(),
                'category': crawled['category'],
                'user_id': str(user_id),
                'source_type': 'web_crawl',
                'crawled_id': crawled_id
            }
        )
        
        chunks = text_splitter.split_documents([doc])
        
        # Add to vectorstore
        user_vectorstore = get_user_vectorstore(user_id)
        if user_vectorstore:
            user_vectorstore.add_documents(chunks)
            
            # Update status to 'ingested'
            CrawledUrl.update_status(crawled_id, 'ingested')
            
            return jsonify({
                "message": f"URL {crawled['url']} ingested successfully. Added {len(chunks)} chunks.",
                "chunks_added": len(chunks),
                "status": "ingested"
            })
        else:
            return jsonify({"error": "Failed to access knowledge base"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500
```

### Step 6: Create Delete Endpoint

**File:** `blueprints/api.py`

```python
@api_bp.route("/api/crawled-urls/<int:crawled_id>", methods=["DELETE"])
@login_required
def delete_crawled_url(crawled_id):
    """Delete crawled URL (and remove from vectorstore if ingested)"""
    try:
        user_id = current_user.id
        from models.crawled_url import CrawledUrl
        from services.knowledge_service import remove_file_from_vectorstore
        
        crawled = CrawledUrl.get_by_id(user_id, crawled_id)
        if not crawled:
            return jsonify({"error": "Crawled URL not found"}), 404
        
        # If ingested, remove from vectorstore
        if crawled['status'] == 'ingested':
            remove_file_from_vectorstore(user_id, crawled['url'])
        
        # Delete from database
        success = CrawledUrl.delete(crawled_id)
        
        if success:
            return jsonify({
                "message": f"URL {crawled['url']} deleted successfully"
            })
        else:
            return jsonify({"error": "Failed to delete"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500
```

### Step 7: Update UI - Add Crawled URLs Overview

**File:** `templates/components/dashboard_knowledge_tab.html`

Add crawled URLs section after uploaded files:
```html
<!-- Crawled URLs -->
<div class="card" style="margin-top: 20px;">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
        <h2 style="margin: 0;">
            <span class="material-icons-round" style="vertical-align: middle; font-size: 24px;">language</span> 
            Crawled Websites
        </h2>
        <button class="btn btn-secondary" onclick="refreshCrawledUrls()" style="padding: 6px 12px; font-size: 12px;">
            <span class="material-icons-round" style="vertical-align: middle; font-size: 16px;">refresh</span> Refresh
        </button>
    </div>
    <div class="crawled-urls-list" id="crawledUrlsList">
        Loading crawled URLs...
    </div>
</div>
```

### Step 8: Update UI - Preview Modal

**File:** `templates/components/dashboard_knowledge_tab.html`

Add preview modal:
```html
<!-- Crawl Preview Modal -->
<div id="crawlPreviewModal" class="modal" style="display: none;">
    <div class="modal-content" style="max-width: 800px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
            <h2>Crawl Preview</h2>
            <button onclick="closeCrawlPreview()" style="background: none; border: none; font-size: 24px; cursor: pointer;">&times;</button>
        </div>
        
        <div style="margin-bottom: 15px;">
            <strong>URL:</strong> <span id="previewUrl"></span>
            <br>
            <strong>Word Count:</strong> <span id="previewWordCount"></span>
            <br>
            <strong>Character Count:</strong> <span id="previewCharCount"></span>
        </div>
        
        <div style="margin-bottom: 15px;">
            <label><strong>Extracted Text (Preview):</strong></label>
            <textarea id="previewText" class="form-control" rows="15" style="font-family: monospace; font-size: 12px;"></textarea>
            <small style="color: #666;">You can edit this text before saving. Only the first 2000 characters are shown in preview.</small>
        </div>
        
        <div style="display: flex; gap: 12px; justify-content: flex-end;">
            <button class="btn btn-secondary" onclick="closeCrawlPreview()">Cancel</button>
            <button class="btn" onclick="saveCrawledContent()">Save to Knowledge Base</button>
        </div>
    </div>
</div>
```

### Step 9: Update JavaScript - Crawl Flow

**File:** `static/js/dashboard/file_management.js`

```javascript
let crawledPreviewData = null;

async function crawlUrl() {
    const urlInput = document.getElementById('urlInput');
    const crawlBtn = document.getElementById('crawlBtn');
    const crawlLoading = document.getElementById('crawlLoading');
    const crawlError = document.getElementById('crawlError');
    
    if (!urlInput) return;
    
    const url = urlInput.value.trim();
    if (!url) {
        if (crawlError) {
            crawlError.textContent = 'Please enter a valid URL';
            crawlError.style.display = 'block';
        }
        return;
    }
    
    if (crawlError) crawlError.style.display = 'none';
    if (crawlBtn) crawlBtn.disabled = true;
    if (crawlLoading) crawlLoading.style.display = 'block';
    
    try {
        // Call preview endpoint (saves to DB, status='preview')
        const response = await fetch('/api/crawl-preview', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                url: url,
                category: selectedCategory || 'company_details'
            })
        });
        
        const result = await response.json();
        
        if (response.ok) {
            // Show preview modal
            crawledPreviewData = result;
            showCrawlPreview(result);
            
            // Clear input
            urlInput.value = '';
            
            // Refresh crawled URLs list
            await refreshCrawledUrls();
        } else {
            throw new Error(result.error || 'Failed to crawl URL');
        }
    } catch (error) {
        if (crawlError) {
            crawlError.textContent = 'Failed to crawl URL: ' + error.message;
            crawlError.style.display = 'block';
        }
    }
    
    if (crawlBtn) crawlBtn.disabled = false;
    if (crawlLoading) crawlLoading.style.display = 'none';
}

function showCrawlPreview(data) {
    document.getElementById('previewUrl').textContent = data.url;
    document.getElementById('previewWordCount').textContent = data.word_count;
    document.getElementById('previewCharCount').textContent = data.char_count;
    document.getElementById('previewText').value = data.full_text; // Full text for editing
    document.getElementById('crawlPreviewModal').style.display = 'block';
}

function closeCrawlPreview() {
    document.getElementById('crawlPreviewModal').style.display = 'none';
    crawledPreviewData = null;
}

async function ingestCrawledContent() {
    const editedText = document.getElementById('previewText').value;
    const crawledId = crawledPreviewData.id;
    
    const response = await fetch(`/api/crawled-urls/${crawledId}/ingest`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            text: editedText
        })
    });
    
    const result = await response.json();
    
    if (response.ok) {
        showAlert('crawlSuccess', result.message);
        closeCrawlPreview();
        await refreshCrawledUrls();
        await refreshFileList(); // Refresh file list too
    } else {
        showAlert('crawlError', result.error || 'Failed to ingest');
    }
}

async function refreshCrawledUrls() {
    try {
        const response = await fetch('/api/crawled-urls');
        const data = await response.json();
        
        const listDiv = document.getElementById('crawledUrlsList');
        if (!listDiv) return;
        
        if (data.urls.length === 0) {
            listDiv.innerHTML = '<div style="text-align: center; color: #999; padding: 20px;">No crawled URLs yet</div>';
            return;
        }
        
        const html = data.urls.map(url => {
            const statusBadge = url.status === 'ingested' 
                ? '<span style="background: #28a745; color: white; padding: 2px 8px; border-radius: 4px; font-size: 11px;">Ingested</span>'
                : '<span style="background: #ffc107; color: #000; padding: 2px 8px; border-radius: 4px; font-size: 11px;">Preview</span>';
            
            return `
                <div class="crawled-url-item" style="display: flex; justify-content: space-between; align-items: center; padding: 12px; border-bottom: 1px solid #e1e5e9;">
                    <div style="flex: 1;">
                        <div style="font-weight: 600; margin-bottom: 4px;">${url.url}</div>
                        <div style="font-size: 12px; color: #666;">
                            ${statusBadge} • ${url.word_count} words • ${new Date(url.crawled_at).toLocaleDateString()}
                        </div>
                    </div>
                    <div style="display: flex; gap: 8px;">
                        <button class="btn btn-secondary" onclick="viewCrawledUrl(${url.id})" style="padding: 6px 12px; font-size: 12px;">
                            <span class="material-icons-round" style="font-size: 16px;">visibility</span> View
                        </button>
                        <button class="btn btn-danger" onclick="deleteCrawledUrl(${url.id})" style="padding: 6px 12px; font-size: 12px;">
                            <span class="material-icons-round" style="font-size: 16px;">delete</span> Delete
                        </button>
                    </div>
                </div>
            `;
        }).join('');
        
        listDiv.innerHTML = html;
    } catch (error) {
        console.error('Failed to load crawled URLs:', error);
    }
}

async function viewCrawledUrl(crawledId) {
    try {
        const response = await fetch(`/api/crawled-urls/${crawledId}`);
        const data = await response.json();
        
        if (response.ok) {
            crawledPreviewData = data;
            showCrawlPreview(data);
        } else {
            alert('Failed to load crawled URL: ' + data.error);
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

async function deleteCrawledUrl(crawledId) {
    if (!confirm('Are you sure you want to delete this crawled URL?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/crawled-urls/${crawledId}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (response.ok) {
            await refreshCrawledUrls();
            showAlert('crawlSuccess', result.message);
        } else {
            showAlert('crawlError', result.error || 'Failed to delete');
        }
    } catch (error) {
        showAlert('crawlError', 'Error: ' + error.message);
    }
}
```

---

## 📚 Required Libraries

### Primary
- **trafilatura** - Best text extraction
- **html2text** - Fallback extraction
- **beautifulsoup4** - HTML parsing (if needed)
- **requests** - HTTP requests

### Text Cleaning
- **unicodedata** - Built-in Python
- **re** - Built-in Python

**Install:**
```bash
pip install trafilatura html2text beautifulsoup4 requests
```

---

## 🧹 Text Cleaning Functions

### 1. Remove HTML Artifacts
- Remove all HTML tags
- Remove script/style content
- Remove comments

### 2. Fix Broken Words
- Join words split across lines (e.g., "exam-\nple" → "example")
- Fix hyphenated words at line breaks

### 3. Encoding Fixes
- Normalize Unicode (NFKD)
- Fix common encoding issues
- Handle special characters

### 4. Whitespace Cleanup
- Remove extra spaces
- Fix multiple newlines
- Trim edges

### 5. Content Quality
- Remove navigation menus
- Remove ads
- Keep only main content
- Preserve structure (headings, lists)

---

## 🎨 UI Flow

1. **User enters URL** → Clicks "Crawl"
2. **System extracts text** → Shows preview modal
3. **User reviews text** → Can edit if needed
4. **User clicks "Save"** → Content saved to knowledge base
5. **Success message** → Chunks added notification

---

## ✅ Benefits

1. **Clean Text:**
   - No broken words
   - No HTML artifacts
   - Proper encoding
   - Better RAG performance

2. **User Control:**
   - Preview before saving
   - Edit if needed
   - Verify quality
   - Better user experience

3. **Better Extraction:**
   - Trafilatura for main content
   - Removes boilerplate automatically
   - Handles encoding well
   - Fast and reliable

---

## 🔄 Implementation Steps

1. **Install libraries** (`trafilatura`, `html2text`)
2. **Create text cleaning service**
3. **Create preview endpoint** (`/api/crawl-preview`)
4. **Create save endpoint** (`/api/crawl-save`)
5. **Update UI** (add preview modal)
6. **Update JavaScript** (preview flow)
7. **Test with various websites**
8. **Iterate based on results**

---

## 🧪 Testing Strategy

Test with:
- Simple HTML pages
- JavaScript-heavy sites (may need Selenium)
- PDF-like content
- Multi-language sites
- Sites with encoding issues
- Sites with lots of ads/navigation

---

**Next Steps:** Implement text cleaning service and preview functionality.

