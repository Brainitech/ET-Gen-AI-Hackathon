"""FastAPI endpoint — Article Search (used by Vernacular Engine)"""
from fastapi import APIRouter, Query
from app.services.rss_service import search_articles, fetch_article_text

router = APIRouter(prefix="/articles", tags=["Article Search"])


@router.get("/search")
def search(q: str = Query(..., min_length=2, description="Search query")):
    """Search ET RSS feeds and return matching article metadata."""
    articles = search_articles(q, max_results=10)
    return {"query": q, "count": len(articles), "articles": articles}


@router.get("/fetch")
def fetch(url: str = Query(..., description="Article URL to scrape")):
    """Fetch full article text from a URL."""
    text = fetch_article_text(url)
    if not text:
        return {"error": "Could not fetch article. Try pasting the text directly.", "text": ""}
    return {"text": text, "char_count": len(text)}
