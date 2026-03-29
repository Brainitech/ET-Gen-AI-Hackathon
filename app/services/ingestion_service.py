"""
ET_Intelligence — Background News Ingestion Service
Polls RSS feeds periodically, extracts full text, runs NLP, generates embeddings,
and stores everything in a local SQLite database for hybrid retrieval.
"""
import asyncio
import json
import sqlite3
import time
import feedparser
from typing import List, Dict, Any
from pathlib import Path

from app.core.config import get_llm_client
from app.services.rss_service import fetch_article_text

# Import NLP helpers dynamically to avoid circular issues
from app.services.story_arc_service import _extract_entities_spacy, _score_sentiment

DB_PATH = Path("news_archive.db")

FEEDS = [
    "https://economictimes.indiatimes.com/rssfeedstopstories.cms",
    "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",
    "https://economictimes.indiatimes.com/tech/rssfeeds/13357270.cms",
    "https://www.reutersagency.com/feed/?best-topics=business-finance&type=rss",
    "https://feeds.bloomberg.com/markets/news.rss"
]

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS news (
                url TEXT PRIMARY KEY,
                title TEXT,
                summary TEXT,
                full_text TEXT,
                published_date TEXT,
                source TEXT,
                entities TEXT,
                sentiment_score REAL,
                embedding TEXT,
                ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

def _is_ingested(url: str) -> bool:
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("SELECT 1 FROM news WHERE url = ?", (url,))
        return cursor.fetchone() is not None

def generate_embedding(text: str) -> List[float]:
    """Generate generic embeddings via the configured local LLM."""
    try:
        client, model = get_llm_client()
        # Ensure we pass a reasonable chunk to the embedding model
        resp = client.embeddings.create(input=text[:3000], model=model)
        return resp.data[0].embedding
    except Exception as e:
        print(f"Embedding error: {e}")
        return []

def process_and_store_article(entry: Dict, source: str):
    url = entry.get("link", "")
    if not url or _is_ingested(url):
        return

    # 1. Fetch text natively via Trafilatura / Playwright bypass
    full_text = fetch_article_text(url)
    if not full_text:
        full_text = entry.get("summary", entry.get("description", ""))
    
    if len(full_text.strip()) < 50:
        return # Too short or fully paywalled

    title = entry.get("title", "")
    summary = entry.get("summary", "")[:500]
    published = entry.get("published", entry.get("updated", ""))

    text_for_nlp = title + " " + full_text

    # 2. NLP Extraction using SpaCy and VADER
    entities = _extract_entities_spacy(text_for_nlp)
    sentiment = _score_sentiment(text_for_nlp)

    # 3. Vector Embedding natively via Ollama
    emb = generate_embedding(text_for_nlp)
    if not emb:
        return # Skip if embedding failed entirely

    # 4. Save to Semantic Index DB
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute('''
            INSERT INTO news (url, title, summary, full_text, published_date, source, entities, sentiment_score, embedding)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            url,
            title,
            summary,
            full_text,
            published,
            source,
            json.dumps(entities),
            sentiment,
            json.dumps(emb)
        ))
    print(f"✅ Ingested to Vector DB: [{source}] {title[:60]}...")

def _ingestion_job():
    print(f"🚀 Starting Background Hybrid News Ingestion Job at {time.ctime()}")
    init_db()
    for feed_url in FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            source_name = feed.feed.get("title", feed_url.split("/")[2])
            # Fetch top 5 per feed per 30 mins to avoid immediate overwhelming
            for entry in feed.entries[:5]: 
                process_and_store_article(entry, source_name)
        except Exception as e:
            print(f"Error parsing feed {feed_url}: {e}")
    print("🏁 Ingestion Job Block Complete.")

async def start_ingestion_worker():
    """To be called in FastAPI Lifespan. Sleeps 30 minutes between sweeps."""
    # Run once immediately, then loop
    await asyncio.to_thread(_ingestion_job)
    while True:
        await asyncio.sleep(1800) # 30 mins
        await asyncio.to_thread(_ingestion_job)
