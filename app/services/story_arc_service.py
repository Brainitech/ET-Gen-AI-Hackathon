"""
aether_ai — Story Arc Tracker Service

Given a topic (e.g. "Adani Group"), fetches related ET articles and produces:
  - timeline of key dated events
  - key players (persons & organisations)
  - sentiment trend over time (VADER)
  - contrarian perspective
  - what-to-watch predictions
"""
import json
import re
import sqlite3
import numpy as np
import concurrent.futures
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, ValidationError
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from app.core.config import get_llm_client
from app.services.rss_service import search_articles, fetch_article_text

_sia = SentimentIntensityAnalyzer()
_nlp = None

# ── Pydantic Models for JSON Validation ───────────────────────────────────────
class TimelineEvent(BaseModel):
    date: str
    event: str
    significance: str

class KeyPlayer(BaseModel):
    name: str
    role: str
    stance: str

class StoryArcSchema(BaseModel):
    timeline: List[TimelineEvent] = Field(default_factory=list)
    key_players: List[KeyPlayer] = Field(default_factory=list)
    sentiment_trend: str = "mixed"
    sentiment_summary: str = ""
    contrarian_view: str = ""
    predictions: str = ""


# ── NER helpers (cached loading) ──────────────────────────────────────────────
def _get_spacy():
    global _nlp
    if _nlp is None:
        try:
            import spacy
            _nlp = spacy.load("en_core_web_sm")
        except Exception:
            _nlp = False
    return _nlp


def _extract_entities_spacy(text: str) -> Dict[str, List[str]]:
    """Extract PERSON and ORG entities using cached spaCy model."""
    nlp = _get_spacy()
    if not nlp:
        return {"persons": [], "orgs": []}
    
    doc = nlp(text[:8000]) # Increased limit slightly for better coverage 
    persons = list({ent.text.strip() for ent in doc.ents if ent.label_ == "PERSON"})
    orgs = list({ent.text.strip() for ent in doc.ents if ent.label_ == "ORG"})
    return {"persons": persons[:8], "orgs": orgs[:8]}


def _extract_event_sentences(text: str, topic: str) -> List[str]:
    """Extract sentences bounded by dates and actions for strict temporal context"""
    nlp = _get_spacy()
    if not nlp:
        # Fallback to crude sentence splitting
        return [s.strip() for s in text.split('.') if len(s.strip()) > 20][:10]

    doc = nlp(text[:8000])
    topic_lower = topic.lower()
    topic_words = set(w for w in topic_lower.split() if w.strip())
    
    events = []
    for sent in doc.sents:
        # Require a DATE or TIME entity in the sentence
        has_date = any(ent.label_ in ("DATE", "TIME") for ent in sent.ents)
        
        sent_lower = sent.text.lower()
        has_topic = topic_lower in sent_lower or any(w in sent_lower for w in topic_words)
        
        if has_date and has_topic:
            events.append(sent.text.strip())
            
    # Include the first two sentences as general context, followed by the specific temporal events
    sents_list = list(doc.sents)
    context_sents = [sents_list[0].text.strip()] if len(sents_list) > 0 else []
    if len(sents_list) > 1:
        context_sents.append(sents_list[1].text.strip())
        
    return context_sents + events


def _score_sentiment(text: str) -> float:
    """Return VADER compound score in [-1, 1]."""
    return _sia.polarity_scores(text)["compound"]


def _fetch_single_article(article: Dict) -> Dict:
    """Helper to fetch article text safely for parallel execution."""
    try:
        text = fetch_article_text(article["link"])
        article["full_text"] = text if text else article.get("summary", "")
    except Exception:
        article["full_text"] = article.get("summary", "")
    return article


def _build_context(articles: List[Dict], topic: str) -> str:
    """Flatten articles into a numbered context block for the LLM using pre-extracted active sentences."""
    lines = []
    for i, a in enumerate(articles, 1):
        pub = a.get("published_date") or a.get("published") or ""
        pub = pub[:16]
        full_text = a.get("full_text") or a.get("summary", "")
        
        event_sents = _extract_event_sentences(full_text, topic)
        if event_sents:
            content_snippet = " ".join(event_sents)[:1000]
        else:
            content_snippet = full_text[:600]
            
        lines.append(f"[{i}] ({pub}) {a.get('title', '')} — {content_snippet}")
    return "\n".join(lines)


def _cosine_similarity(a: List[float], b: List[float]) -> float:
    a_arr = np.array(a)
    b_arr = np.array(b)
    norm_a = np.linalg.norm(a_arr)
    norm_b = np.linalg.norm(b_arr)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(a_arr, b_arr) / (norm_a * norm_b))


def _search_local_vector_db(topic: str, max_results: int = 5) -> List[Dict]:
    """Retrieve exactly matched articles and re-rank via Semantic Vector Distance."""
    topic_lower = topic.lower()
    
    try:
        from app.services.ingestion_service import generate_embedding, DB_PATH
    except ImportError:
        return []

    topic_emb = generate_embedding(topic)
    if not topic_emb:
        return []

    results = []
    try:
        if not DB_PATH.exists():
            return []
            
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("SELECT * FROM news ORDER BY ingested_at DESC LIMIT 300").fetchall()
            
            for row in rows:
                full_text = (row["full_text"] or "").lower()
                entities_str = (row["entities"] or "").lower()
                
                # Pre-filter exact keyword to avoid hallucinating contexts
                # Ensure all topic words are broadly represented in the body or extracted entities
                words = topic_lower.split()
                if all(w in full_text or w in entities_str for w in words):
                    try:
                        art_emb = json.loads(row["embedding"])
                        sim = _cosine_similarity(topic_emb, art_emb)
                        results.append((sim, dict(row)))
                    except Exception:
                        pass
                        
    except Exception as e:
        print(f"Local Vector DB Error: {e}")
        return []
        
    # Re-rank via semantic similarity
    results.sort(key=lambda x: x[0], reverse=True)
    
    # Adapt DB schema to what the service expects
    adapted = []
    for score, row in results[:max_results]:
        adapted.append({
            "title": row["title"],
            "summary": row["summary"],
            "full_text": row["full_text"],
            "published": row["published_date"],
            "link": row["url"],
            "source": row["source"],
            "is_cached": True,
            "sim_score": score
        })
    return adapted


# ── Main service function ─────────────────────────────────────────────────────
def build_story_arc(topic: str) -> Dict[str, Any]:
    """
    Full Story Arc pipeline, optimized for parallel fetching and strict validation.
    """
    local_articles = _search_local_vector_db(topic, max_results=5)
    
    # Hybrid Fallback trigger
    if len(local_articles) < 3:
        print(f"Hybrid Mode: Only {len(local_articles)} found in cache. Falling back to live search...")
        live_arts = search_articles(topic, max_results=5)
        
        # Parallel article fetching to minimize latency for live fetched
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            live_arts = list(executor.map(_fetch_single_article, live_arts))
            
        seen_urls = {a["link"] for a in local_articles}
        for la in live_arts:
            if la["link"] not in seen_urls:
                la["is_cached"] = False
                local_articles.append(la)
                seen_urls.add(la["link"])

    articles = local_articles[:5]
    if not articles:
        return {"error": "No relevant articles found locally or remotely. Try a different topic."}

    # ── 1. Sentiment per article ───────────────────────────────────────────────
    sentiment_data = []
    for a in articles:
        text = a.get("title", "") + " " + a.get("summary", "")
        score = _score_sentiment(text)
        sentiment_data.append({
            "title": a.get("title", "")[:80],
            "score": round(score, 3),
            "published": a.get("published", ""),
            "link": a.get("link", ""),
        })

    # ── 2. Key players via spaCy NER ──────────────────────────────────────────
    combined_text = " ".join(
        a.get("title", "") + " " + (a.get("full_text") or a.get("summary", "")) for a in articles
    )
    entities = _extract_entities_spacy(combined_text)

    # ── 3. Narrative arc via LLM ──────────────────────────────────────────────
    context = _build_context(articles, topic)
    prompt = f"""You are a business journalist AI. Based on the following Economic Times news articles about "{topic}", produce a structured story arc in pure JSON. Do not hallucinate.

NEWS ARTICLES:
{context}

Return this exact JSON structure:
{{
  "timeline": [
    {{"date": "YYYY-MM-DD", "event": "description", "significance": "high|medium|low"}}
  ],
  "key_players": [
    {{"name": "Name", "role": "Role", "stance": "positive|negative|neutral"}}
  ],
  "sentiment_trend": "rising|falling|mixed|stable",
  "sentiment_summary": "2-sentence explanation.",
  "contrarian_view": "2-sentence alternative perspective.",
  "predictions": "2-sentence prediction of what to watch out for next based on these facts."
}}

Rules:
- STRICTLY rely ONLY on the provided NEWS ARTICLES facts.
- timeline events MUST be chronological.
- Return valid JSON ONLY. No markdown."""

    client, model = get_llm_client()
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1, # Lower temperature for zero-hallucination
            max_tokens=1500,
            response_format={"type": "json_object"}
        )
        raw = resp.choices[0].message.content.strip()
        
        # Robustly extract the JSON block regardless of markdown wrapping or conversational prefaces
        json_match = re.search(r'\{.*\}', raw, re.DOTALL)
        clean_json = json_match.group(0) if json_match else raw
        
        # Strict validation using Pydantic
        parsed_json = json.loads(clean_json)
        validated_data = StoryArcSchema(**parsed_json).model_dump()
        arc_data = validated_data
        
    except (json.JSONDecodeError, ValidationError) as e:
        arc_data = StoryArcSchema(
            sentiment_summary=f"Parsing error: {str(e)}",
            contrarian_view="Analysis unavailable due to strict validation failure.",
            predictions="Data unavailable."
        ).model_dump()
    except Exception as e:
        arc_data = StoryArcSchema(
            sentiment_summary=f"LLM error: {str(e)}",
            contrarian_view="LLM unavailable.",
            predictions="System offline."
        ).model_dump()

    # Merge NER entities that might be missed by LLM
    existing_names = {p["name"].lower() for p in arc_data.get("key_players", [])}
    for person in entities.get("persons", []):
        if person.lower() not in existing_names:
            arc_data.setdefault("key_players", []).append(
                {"name": person, "role": "Key Person", "stance": "neutral"}
            )
            existing_names.add(person.lower())

    latest_pub = max((a.get("published", "") for a in articles if a.get("published")), default="")

    cached_count = sum(1 for a in articles if a.get("is_cached"))
    data_source_badge = "⚡ Local Semantic Cache" if cached_count >= 3 else "🌐 Live Hybrid Search"

    return {
        "topic": topic,
        "article_count": len(articles),
        "data_source_badge": data_source_badge,
        "last_updated": latest_pub,
        "sentiment_data": sentiment_data,
        "timeline": arc_data.get("timeline", []),
        "key_players": arc_data.get("key_players", []),
        "sentiment_trend": arc_data.get("sentiment_trend", "mixed"),
        "sentiment_summary": arc_data.get("sentiment_summary", ""),
        "contrarian_view": arc_data.get("contrarian_view", ""),
        "predictions": arc_data.get("predictions", ""),
    }
