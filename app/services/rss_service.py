"""
aether_ai — Shared RSS Service
Fetches and keyword-filters Economic Times articles from RSS feeds.
Results are cached in-memory for 5 minutes to avoid hammering RSS.
"""
import time
import feedparser
import requests
import re
from typing import List, Dict, Any
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


def _parse_feed(url: str) -> List[Dict]:
    """Parse a single RSS feed and return normalised article dicts."""
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
    """Fetch all ET RSS feeds, deduplicated, cached for 5 min."""
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
    """
    Return articles whose title or summary contain any query keyword.
    Falls back to most-recent articles if nothing matches.
    """
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

    # Fallback: return latest articles when no match
    if not results:
        results = all_arts

    return results[:max_results]


def fetch_article_text(url: str) -> str:
    """
    Scrape full article text from a URL.
    Tries ET-specific CSS selectors first, then falls back to long <p> tags.
    """
    try:
        from bs4 import BeautifulSoup
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            ),
            "Referer": "https://economictimes.indiatimes.com/",
            "Accept-Language": "en-US,en;q=0.9",
        }
        resp = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        # Remove noise elements
        for tag in soup(["script", "style", "nav", "header", "footer",
                          "aside", "noscript", "iframe", "figure", "figcaption"]):
            tag.decompose()

        # ── Strategy 1: ET-specific article body selectors ────────────────────
        ET_SELECTORS = [
            "[itemprop='articleBody']",   # Standard article markup
            ".artText",                    # Classic ET selector
            "div.Normal",                  # ET article paragraphs
            "div[class*='artText']",       # Variant spellings
            "div[class*='article-body']",  # Some ET subdomains
            "div[class*='articleBody']",
            "div[class*='story-content']",
            "article",                     # HTML5 semantic
        ]
        for selector in ET_SELECTORS:
            el = soup.select_one(selector)
            if el:
                text = el.get_text(" ", strip=True)
                if len(text) > 200:           # Ignore tiny matches
                    return text[:8000]

        # ── Strategy 2: Collect long <p> tags (ignore nav/footer noise) ───────
        paragraphs = [
            p.get_text(" ", strip=True)
            for p in soup.find_all("p")
            if len(p.get_text(strip=True)) > 60   # Skip short/nav paragraphs
        ]
        if paragraphs:
            return " ".join(paragraphs)[:8000]

        return ""
    except Exception:
        return ""

