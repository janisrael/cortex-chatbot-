# 🕷️ Clean Web Crawling & Text Extraction Plan

**Version:** 1.0  
**Date:** 2025-11-23  
**Status:** Planning

---

## 🎯 Problem Statement

Current crawling implementation has issues:
- **Broken words** in extracted text
- **HTML artifacts** not properly removed
- **Encoding issues** causing garbled text
- **No preview** before saving to knowledge base
- **Poor text quality** affecting RAG performance

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

## 🛠️ Implementation Plan

### Step 1: Create Text Cleaning Service

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

### Step 2: Create Preview Endpoint

**File:** `blueprints/api.py`

```python
@api_bp.route("/api/crawl-preview", methods=["POST"])
@login_required
def crawl_url_preview():
    """Preview crawled content before saving"""
    try:
        data = request.json
        url = data.get('url')
        
        if not url:
            return jsonify({"error": "No URL provided"}), 400
        
        # Extract clean text
        from services.text_cleaning_service import extract_clean_text_from_url
        
        text = extract_clean_text_from_url(url)
        
        if not text:
            return jsonify({"error": "Failed to extract content from URL"}), 400
        
        # Get text stats
        word_count = len(text.split())
        char_count = len(text)
        preview_length = 2000  # First 2000 chars for preview
        
        return jsonify({
            "url": url,
            "preview": text[:preview_length],
            "full_text": text,  # For saving later
            "word_count": word_count,
            "char_count": char_count,
            "preview_only": len(text) > preview_length
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
```

### Step 3: Update Save Endpoint

**File:** `blueprints/api.py`

```python
@api_bp.route("/api/crawl-save", methods=["POST"])
@login_required
def crawl_url_save():
    """Save previewed crawled content to knowledge base"""
    try:
        data = request.json
        url = data.get('url')
        text = data.get('text')  # User may have edited it
        category = data.get('category', 'company_details')
        
        if not url or not text:
            return jsonify({"error": "URL and text required"}), 400
        
        user_id = current_user.id
        
        # Split into chunks
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        from services.knowledge_service import get_user_vectorstore, embeddings
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        
        # Create document from cleaned text
        from langchain.schema import Document
        doc = Document(
            page_content=text,
            metadata={
                'source_file': url,
                'upload_time': datetime.now().isoformat(),
                'category': category,
                'user_id': str(user_id),
                'source_type': 'web_crawl'
            }
        )
        
        chunks = text_splitter.split_documents([doc])
        
        # Add to vectorstore
        user_vectorstore = get_user_vectorstore(user_id)
        if user_vectorstore:
            user_vectorstore.add_documents(chunks)
            return jsonify({
                "message": f"URL {url} saved successfully. Added {len(chunks)} chunks.",
                "chunks_added": len(chunks)
            })
        else:
            return jsonify({"error": "Failed to access knowledge base"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500
```

### Step 4: Update UI with Preview

**File:** `templates/components/dashboard_knowledge_tab.html`

Add preview section:
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

### Step 5: Update JavaScript

**File:** `static/js/dashboard/file_management.js`

```javascript
let crawledPreviewData = null;

async function crawlUrl() {
    // ... existing code ...
    
    // Change to preview endpoint
    const response = await fetch('/api/crawl-preview', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: url })
    });
    
    const result = await response.json();
    
    if (response.ok) {
        // Show preview modal
        crawledPreviewData = result;
        showCrawlPreview(result);
    } else {
        // Show error
    }
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

async function saveCrawledContent() {
    const editedText = document.getElementById('previewText').value;
    
    const response = await fetch('/api/crawl-save', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            url: crawledPreviewData.url,
            text: editedText,
            category: 'company_details'
        })
    });
    
    // Handle response...
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

