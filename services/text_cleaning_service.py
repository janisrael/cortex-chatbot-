"""
Text Cleaning Service for Web Crawling
Extracts clean text from URLs using Trafilatura and html2text
"""
import os
import re
import unicodedata
import requests
from html2text import HTML2Text

JINA_READER_BASE = "https://r.jina.ai/"


def clean_extracted_text(text):
    """Clean extracted text from web pages"""
    if not text:
        return ""
    
    # Remove markdown link references at the end (e.g., [1]: /, [2]: /blog)
    # These are usually at the bottom of html2text output
    text = re.sub(r'\n\s*\[(\d+)\]:\s*[^\n]+\s*', '\n', text)
    text = re.sub(r'\[(\d+)\]:\s*[^\n]+', '', text)
    
    # Remove markdown-style links [text][number] or [text](url)
    # Replace with just the text part
    text = re.sub(r'\[([^\]]+)\]\[\d+\]', r'\1', text)  # [text][1] -> text
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)  # [text](url) -> text
    
    # Remove markdown image syntax ![alt](url)
    text = re.sub(r'!\[([^\]]*)\]\([^\)]+\)', r'\1', text)
    
    # Remove markdown headers (# ## ###)
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    
    # Remove markdown bold/italic markers (keep the text)
    text = re.sub(r'\*\*([^\*]+)\*\*', r'\1', text)  # **bold** -> bold
    text = re.sub(r'\*([^\*]+)\*', r'\1', text)  # *italic* -> italic
    text = re.sub(r'__([^_]+)__', r'\1', text)  # __bold__ -> bold
    text = re.sub(r'_([^_]+)_', r'\1', text)  # _italic_ -> italic
    
    # Remove broken words (words split across lines with hyphen)
    # Example: "exam-\nple" -> "example"
    text = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', text)
    
    # Fix common encoding issues
    text = unicodedata.normalize('NFKD', text)
    
    # Replace problematic special characters with readable equivalents
    # Replace em dash, en dash with regular dash
    text = text.replace('—', '-').replace('–', '-')
    # Replace smart quotes with regular quotes
    text = text.replace('"', '"').replace('"', '"')
    text = text.replace(''', "'").replace(''', "'")
    # Replace ellipsis
    text = text.replace('…', '...')
    
    # Remove or replace other problematic unicode characters
    # Keep common punctuation but remove weird symbols
    text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)\[\]\'\"\/\@\#\$\%\&\*\+\=\n]', ' ', text)
    
    # Fix multiple spaces (but preserve newlines for structure)
    text = re.sub(r' +', ' ', text)
    
    # Fix multiple newlines (keep max 2 consecutive)
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
    
    # Remove leading/trailing whitespace from each line
    lines = text.split('\n')
    lines = [line.strip() for line in lines if line.strip()]  # Also remove empty lines
    text = '\n'.join(lines)
    
    # Remove empty lines at start and end
    text = text.strip()
    
    # Final cleanup: remove any remaining markdown artifacts
    # Remove standalone numbers in brackets (leftover references)
    text = re.sub(r'\[\d+\]', '', text)
    
    return text


def _jina_fallback_enabled():
    return os.getenv("CRAWL_JINA_FALLBACK", "true").lower() in ("1", "true", "yes", "on")


def _extract_via_jina_reader(url):
    """Fetch page text via Jina Reader (helps with Cloudflare bot challenges)."""
    if not _jina_fallback_enabled():
        return None

    reader_url = f"{JINA_READER_BASE}{url}"
    try:
        print("📥 Trying Jina Reader fallback (Cloudflare bypass)...")
        response = requests.get(
            reader_url,
            timeout=45,
            headers={
                "Accept": "text/plain",
                "User-Agent": "Mozilla/5.0 (compatible; CortexCrawler/1.0; +https://cortex.janisrael.com)",
            },
        )
        response.raise_for_status()
        body = response.text.strip()
        if not body:
            return None

        marker = "Markdown Content:"
        if marker in body:
            text = body.split(marker, 1)[1].strip()
        else:
            text = body

        # Drop markdown image syntax; keep link text where possible
        text = re.sub(r"!\[[^\]]*\]\([^\)]+\)", " ", text)
        text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)

        if text and len(text.strip()) > 50:
            print(f"✅ Jina Reader extracted {len(text)} characters")
            return clean_extracted_text(text)
        print(f"⚠️ Jina Reader returned too little content ({len(text) if text else 0} chars)")
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Jina Reader request failed for {url}: {e}")
    except Exception as e:
        print(f"⚠️ Jina Reader fallback failed for {url}: {e}")
    return None


def extract_clean_text_from_url(url):
    """Extract clean text from URL using best available method"""
    print(f"🔍 Attempting to extract text from: {url}")
    
    try:
        # Try Trafilatura first (best for most sites)
        import trafilatura
        from copy import deepcopy
        from trafilatura.settings import DEFAULT_CONFIG

        config = deepcopy(DEFAULT_CONFIG)
        config.set("DEFAULT", "DOWNLOAD_TIMEOUT", "15")

        print(f"📥 Fetching URL with Trafilatura...")
        downloaded = trafilatura.fetch_url(url, config=config)
        
        if downloaded:
            print(f"✅ Content fetched, extracting text...")
            text = trafilatura.extract(
                downloaded,
                include_comments=False,
                include_tables=False,
                include_images=False,
                include_links=False,
                no_fallback=False
            )
            
            if text and len(text.strip()) > 50:  # Minimum content check
                print(f"✅ Trafilatura extracted {len(text)} characters")
                return clean_extracted_text(text)
            else:
                print(f"⚠️ Trafilatura extracted too little content ({len(text) if text else 0} chars)")
        else:
            print(f"⚠️ Trafilatura failed to fetch URL")
    except Exception as e:
        print(f"⚠️ Trafilatura failed for {url}: {e}")
        import traceback
        traceback.print_exc()
    
    try:
        # Fallback to html2text
        print(f"📥 Trying html2text fallback...")
        response = requests.get(
            url, 
            timeout=15, 
            headers={
                'User-Agent': (
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                    '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                ),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
            },
            allow_redirects=True
        )
        response.raise_for_status()
        
        print(f"✅ HTML fetched ({len(response.text)} chars), converting to text...")
        h = HTML2Text()
        h.ignore_links = False
        h.ignore_images = True
        h.ignore_emphasis = False
        h.body_width = 0  # Don't wrap
        h.unicode_snob = True  # Use unicode
        h.skip_internal_links = True
        h.inline_links = False
        
        text = h.handle(response.text)
        
        if text and len(text.strip()) > 50:
            print(f"✅ html2text extracted {len(text)} characters")
            return clean_extracted_text(text)
        print(f"⚠️ html2text extracted too little content ({len(text.strip()) if text else 0} chars)")
    except requests.exceptions.RequestException as e:
        print(f"⚠️ html2text HTTP request failed for {url}: {e}")
    except Exception as e:
        print(f"⚠️ html2text fallback failed for {url}: {e}")
        import traceback
        traceback.print_exc()

    jina_text = _extract_via_jina_reader(url)
    if jina_text:
        return jina_text

    print(f"❌ All extraction methods failed for {url}")
    return None

