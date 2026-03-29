"""FastAPI endpoint — Article Search (used by Vernacular Engine)"""
from fastapi import APIRouter, Query
from app.services.rss_service import search_articles, fetch_article_text, poll_et_feeds, fetch_all_articles

router = APIRouter(prefix="/articles", tags=["Article Search"])


@router.get("/search")
def search(q: str = Query(..., min_length=2, description="Search query")):
    """Search ET RSS feeds and return matching article metadata."""
    articles = search_articles(q, max_results=10)
    return {"query": q, "count": len(articles), "articles": articles}


@router.get("/feed")
def get_feed(max_per_feed: int = Query(default=15, description="Max articles per RSS feed")):
    """Fetch all live ET RSS feeds and return articles for the home page general feed."""
    articles = fetch_all_articles(max_per_feed=max_per_feed)
    return {"count": len(articles), "articles": articles}


@router.get("/fetch")
def fetch(url: str = Query(..., description="Article URL to scrape")):
    """Fetch full article text from a URL."""
    text = fetch_article_text(url)
    if not text:
        return {"error": "Could not fetch article. Try pasting the text directly.", "text": ""}
    return {"text": text, "char_count": len(text)}


@router.get("/pipeline_test")
def test_pipeline():
    """Run the hybrid extractor on the RSS feeds."""
    articles = poll_et_feeds(max_per_feed=1)
    return {"count": len(articles), "articles": articles}
