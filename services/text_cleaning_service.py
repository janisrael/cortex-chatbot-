"""
Text Cleaning Service for Web Crawling
Extracts clean text from URLs using Trafilatura and html2text
"""
import os
import re
import unicodedata
from copy import deepcopy
from urllib.parse import urlparse

import requests
from html2text import HTML2Text

JINA_READER_BASE = "https://r.jina.ai/"
_MIN_TEXT_CHARS = int(os.getenv("CRAWL_MIN_TEXT_CHARS", "50"))
_last_extraction_diagnostics = []


def get_extraction_diagnostics():
    return list(_last_extraction_diagnostics)


def _record(step, status, detail=""):
    _last_extraction_diagnostics.append({"step": step, "status": status, "detail": str(detail)[:500]})


def normalize_crawl_url(url):
    url = (url or "").strip()
    if not url:
        return url
    if not url.lower().startswith(("http://", "https://")):
        url = "https://" + url
    return url


def clean_extracted_text(text):
    """Clean extracted text from web pages"""
    if not text:
        return ""

    text = re.sub(r'\n\s*\[(\d+)\]:\s*[^\n]+\s*', '\n', text)
    text = re.sub(r'\[(\d+)\]:\s*[^\n]+', '', text)
    text = re.sub(r'\[([^\]]+)\]\[\d+\]', r'\1', text)
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    text = re.sub(r'!\[([^\]]*)\]\([^\)]+\)', r'\1', text)
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\*\*([^\*]+)\*\*', r'\1', text)
    text = re.sub(r'\*([^\*]+)\*', r'\1', text)
    text = re.sub(r'__([^_]+)__', r'\1', text)
    text = re.sub(r'_([^_]+)_', r'\1', text)
    text = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', text)
    text = unicodedata.normalize('NFKD', text)
    text = text.replace('—', '-').replace('–', '-')
    text = text.replace('"', '"').replace('"', '"')
    text = text.replace(''', "'").replace(''', "'")
    text = text.replace('…', '...')
    text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)\[\]\'\"\/\@\#\$\%\&\*\+\=\n]', ' ', text)
    text = re.sub(r' +', ' ', text)
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
    lines = text.split('\n')
    lines = [line.strip() for line in lines if line.strip()]
    text = '\n'.join(lines)
    text = text.strip()
    text = re.sub(r'\[\d+\]', '', text)
    return text


def _browser_headers():
    return {
        'User-Agent': (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
            '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
    }


def _looks_like_bot_challenge(html):
    if not html:
        return False
    sample = html[:12000].lower()
    markers = (
        'just a moment',
        'cf-browser-verification',
        'challenge-platform',
        'attention required',
        'enable javascript',
    )
    return any(m in sample for m in markers)


def _text_usable(text):
    cleaned = clean_extracted_text(text) if text else ""
    return cleaned if len(cleaned) >= _MIN_TEXT_CHARS else None


def _fetch_html(url, timeout=None):
    timeout = timeout or int(os.getenv("CRAWL_FETCH_TIMEOUT", "25"))
    session = requests.Session()
    try:
        response = session.get(
            url,
            timeout=timeout,
            headers=_browser_headers(),
            allow_redirects=True,
        )
        _record("http_fetch", "ok", f"status={response.status_code} bytes={len(response.text or '')}")
        response.raise_for_status()
        return response.text, response.status_code
    except requests.exceptions.RequestException as e:
        _record("http_fetch", "failed", e)
        return None, None
    finally:
        session.close()


def _extract_with_trafilatura(html, url):
    if not html:
        return None
    try:
        import trafilatura
        from trafilatura.settings import DEFAULT_CONFIG

        config = deepcopy(DEFAULT_CONFIG)
        config.set("DEFAULT", "DOWNLOAD_TIMEOUT", str(os.getenv("CRAWL_FETCH_TIMEOUT", "25")))

        text = trafilatura.extract(
            html,
            url=url,
            include_comments=False,
            include_tables=True,
            include_images=False,
            include_links=False,
            no_fallback=False,
        )
        if text and len(text.strip()) >= _MIN_TEXT_CHARS:
            _record("trafilatura_extract", "ok", f"chars={len(text)}")
            return clean_extracted_text(text)

        try:
            bare = trafilatura.bare_extraction(html, url=url)
            if bare and bare.get("text") and len(bare["text"].strip()) >= _MIN_TEXT_CHARS:
                _record("trafilatura_bare", "ok", f"chars={len(bare['text'])}")
                return clean_extracted_text(bare["text"])
        except Exception as bare_err:
            _record("trafilatura_bare", "failed", bare_err)

        _record(
            "trafilatura_extract",
            "empty",
            f"primary={len(text.strip()) if text else 0} chars",
        )
    except Exception as e:
        _record("trafilatura_extract", "failed", e)
    return None


def _extract_with_html2text(html):
    if not html:
        return None
    try:
        h = HTML2Text()
        h.ignore_links = False
        h.ignore_images = True
        h.ignore_emphasis = False
        h.body_width = 0
        h.unicode_snob = True
        h.skip_internal_links = True
        h.inline_links = False
        text = h.handle(html)
        usable = _text_usable(text)
        if usable:
            _record("html2text", "ok", f"chars={len(usable)}")
            return usable
        _record("html2text", "empty", len(text.strip()) if text else 0)
    except Exception as e:
        _record("html2text", "failed", e)
    return None


def _jina_fallback_enabled():
    return os.getenv("CRAWL_JINA_FALLBACK", "true").lower() in ("1", "true", "yes", "on")


def _extract_via_jina_reader(url):
    """Fetch page text via Jina Reader (helps with Cloudflare bot challenges)."""
    if not _jina_fallback_enabled():
        _record("jina_reader", "skipped", "CRAWL_JINA_FALLBACK disabled")
        return None

    reader_url = f"{JINA_READER_BASE}{url}"
    try:
        response = requests.get(
            reader_url,
            timeout=int(os.getenv("CRAWL_JINA_TIMEOUT", "60")),
            headers={
                "Accept": "text/plain",
                "User-Agent": "Mozilla/5.0 (compatible; CortexCrawler/1.0; +https://cortex.janisrael.com)",
            },
        )
        _record("jina_reader", "http", f"status={response.status_code}")
        response.raise_for_status()
        body = response.text.strip()
        if not body:
            _record("jina_reader", "empty", "empty body")
            return None

        marker = "Markdown Content:"
        text = body.split(marker, 1)[1].strip() if marker in body else body
        text = re.sub(r"!\[[^\]]*\]\([^\)]+\)", " ", text)
        text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)

        usable = _text_usable(text)
        if usable:
            _record("jina_reader", "ok", f"chars={len(usable)}")
            return usable
        _record("jina_reader", "empty", len(text.strip()) if text else 0)
    except requests.exceptions.RequestException as e:
        _record("jina_reader", "failed", e)
    except Exception as e:
        _record("jina_reader", "failed", e)
    return None


def extract_clean_text_from_url(url):
    """Extract clean text from URL using best available method"""
    global _last_extraction_diagnostics
    _last_extraction_diagnostics = []

    url = normalize_crawl_url(url)
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        _record("validate_url", "failed", url)
        return None

    print(f"🔍 Attempting to extract text from: {url}")

    html = None
    http_status = None

    try:
        import trafilatura
        from trafilatura.settings import DEFAULT_CONFIG

        config = deepcopy(DEFAULT_CONFIG)
        config.set("DEFAULT", "DOWNLOAD_TIMEOUT", str(os.getenv("CRAWL_FETCH_TIMEOUT", "25")))
        downloaded = trafilatura.fetch_url(url, config=config)
        if downloaded:
            _record("trafilatura_fetch", "ok", f"bytes={len(downloaded)}")
            text = _extract_with_trafilatura(downloaded, url)
            if text:
                print(f"✅ Trafilatura pipeline extracted {len(text)} characters")
                return text
            html = downloaded
        else:
            _record("trafilatura_fetch", "empty", "no body")
    except Exception as e:
        _record("trafilatura_fetch", "failed", e)

    if html is None:
        html, http_status = _fetch_html(url)

    use_jina_early = (
        html is None
        or (http_status in (403, 429, 503))
        or _looks_like_bot_challenge(html)
    )
    if use_jina_early:
        jina_text = _extract_via_jina_reader(url)
        if jina_text:
            return jina_text

    if html:
        text = _extract_with_trafilatura(html, url)
        if text:
            print(f"✅ Trafilatura (requests HTML) extracted {len(text)} characters")
            return text

        text = _extract_with_html2text(html)
        if text:
            print(f"✅ html2text extracted {len(text)} characters")
            return text

    jina_text = _extract_via_jina_reader(url)
    if jina_text:
        return jina_text

    print(f"❌ All extraction methods failed for {url}")
    return None