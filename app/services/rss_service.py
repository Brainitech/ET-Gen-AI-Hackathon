"""
ET_Intelligence — Shared RSS Service
Fetches and keyword-filters Economic Times articles from RSS feeds.
Results are cached in-memory. Implements a resilient hybrid extraction strategy
using Trafilatura and Playwright for JS-rendered pages.
"""
import time
import feedparser
import requests
import re
import sqlite3
import random
from typing import List, Dict, Any
from pathlib import Path

import trafilatura
from playwright.sync_api import sync_playwright

from app.core.config import settings

# ── In-memory cache ────────────────────────────────────────────────────────────
_cache: Dict[str, Any] = {}
CACHE_TTL = 300  # 5 minutes

ALL_FEEDS = [
    settings.ET_RSS_MARKETS,
    settings.ET_RSS_TECH,
    settings.ET_RSS_STARTUP,
    settings.ET_RSS_ECONOMY,
    settings.ET_RSS_POLICY,
]

# ── SQLite URL Tracker ─────────────────────────────────────────────────────────

DB_PATH = Path("seen_urls.db")

def init_db():
    """Initializes the SQLite database to track 'seen' URLs."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS seen_urls (
                url TEXT PRIMARY KEY,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

def is_url_seen(url: str) -> bool:
    """Checks if a URL has already been scraped to avoid duplicates."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("SELECT 1 FROM seen_urls WHERE url = ?", (url,))
        return cursor.fetchone() is not None

def mark_url_seen(url: str):
    """Marks a URL as seen in the SQLite tracking database."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("INSERT OR IGNORE INTO seen_urls (url) VALUES (?)", (url,))


# ── Resilience Utilities ───────────────────────────────────────────────────────

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:123.0) Gecko/20100101 Firefox/123.0",
]

def get_random_user_agent() -> str:
    return random.choice(USER_AGENTS)

# ── Extraction Logic ───────────────────────────────────────────────────────────

def fetch_article_text(url: str) -> str:
    """
    Hybrid extraction strategy for overcoming BeautifulSoup walls on ET.
    1. Try Trafilatura directly.
    2. If text < 200 chars, fallback to Playwright headless chromium.
    """
    # ── Strategy 1: Trafilatura Direct ──────────────────────────────────────────
    try:
        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            text = trafilatura.extract(downloaded)
            if text and len(text) >= 200:
                return text
    except Exception as e:
        print(f"Trafilatura direct fetch failed for {url}: {e}")

    # ── Strategy 2: Playwright Fallback ─────────────────────────────────────────
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(user_agent=get_random_user_agent())
            page = context.new_page()
            
            # Load page and ensure JS is painted
            page.goto(url, wait_until="networkidle", timeout=30000)
            
            # Specific ET subdomain structures
            try:
                page.wait_for_selector('div.artText, .article-body, .content', timeout=10000)
            except Exception:
                pass  # Ignore timeout if selector genuinely missing, try parsing anyway
                
            # Extract fully rendered HTML and pass to Trafilatura for clean output
            html = page.content()
            browser.close()
            
            text = trafilatura.extract(html)
            if text:
                return text
    except Exception as e:
        print(f"Playwright fallback failed for {url}: {e}")

    return ""

def poll_et_feeds(max_per_feed: int = 5) -> List[Dict]:
    """
    Poll ET RSS feeds, extract article links, and process them via hybrid pipeline.
    Avoids duplicates using SQLite tracker and avoids IP blocks with a 2-second sleep.
    """
    init_db()
    extracted_articles = []
    
    for feed_url in ALL_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:max_per_feed]:
                url = entry.get("link", "")
                if not url or is_url_seen(url):
                    continue
                
                # Resilience: Sleep to avoid IP blocks
                time.sleep(2)
                
                # Hybrid full-text extraction
                full_text = fetch_article_text(url)
                
                # Structure Output JSON
                article = {
                    "title": entry.get("title", ""),
                    "full_text": full_text,
                    "publish_date": entry.get("published", entry.get("updated", "")),
                    "category": feed.feed.get("title", "ET"),
                    "url": url,
                }
                
                extracted_articles.append(article)
                mark_url_seen(url)
        except Exception as e:
            print(f"Failed to poll feed {feed_url}: {e}")
            
    return extracted_articles

# ── Legacy/UI Adapting Functions ───────────────────────────────────────────────

def _parse_feed(url: str) -> List[Dict]:
    """Parse a single RSS feed and return normalised article dicts for legacy UI."""
    try:
        feed = feedparser.parse(url)
        articles = []
        for entry in feed.entries:
            articles.append({
                "title": entry.get("title", ""),
                "summary": entry.get("summary", entry.get("description", "")),
                "link": entry.get("link", ""),
                "published": entry.get("published", entry.get("updated", "")),
                "source": feed.feed.get("title", "ET"),
            })
        return articles
    except Exception:
        return []

def fetch_all_articles(max_per_feed: int = 15) -> List[Dict]:
    """Fetch all ET RSS feeds, deduplicated, cached for 5 min for front-end."""
    cache_key = "ALL"
    now = time.time()
    if cache_key in _cache and now - _cache[cache_key]["ts"] < CACHE_TTL:
        return _cache[cache_key]["data"]

    seen_links: set = set()
    all_articles: List[Dict] = []
    for url in ALL_FEEDS:
        for art in _parse_feed(url)[:max_per_feed]:
            if art["link"] not in seen_links:
                seen_links.add(art["link"])
                all_articles.append(art)

    _cache[cache_key] = {"ts": now, "data": all_articles}
    return all_articles

def search_articles(query: str, max_results: int = 20) -> List[Dict]:
    """Return articles whose title or summary contain query keyword. Fallback to latest."""
    all_arts = fetch_all_articles()
    keywords = [w.lower() for w in re.split(r"\s+", query.strip()) if len(w) > 2]

    scored: List[tuple] = []
    for art in all_arts:
        text = (art["title"] + " " + art["summary"]).lower()
        score = sum(text.count(kw) for kw in keywords)
        if score > 0:
            scored.append((score, art))

    scored.sort(key=lambda x: x[0], reverse=True)
    results = [a for _, a in scored]

    if not results:
        results = all_arts

    return results[:max_results]
