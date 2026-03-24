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
from datetime import datetime
from typing import Any, Dict, List

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from app.core.config import get_llm_client
from app.services.rss_service import search_articles

_sia = SentimentIntensityAnalyzer()


# ── NER helpers (lightweight, no heavy model download) ────────────────────────
def _extract_entities_spacy(text: str) -> Dict[str, List[str]]:
    """Extract PERSON and ORG entities using spaCy en_core_web_sm."""
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(text[:5000])
        persons = list({ent.text.strip() for ent in doc.ents if ent.label_ == "PERSON"})
        orgs = list({ent.text.strip() for ent in doc.ents if ent.label_ == "ORG"})
        return {"persons": persons[:8], "orgs": orgs[:8]}
    except Exception:
        return {"persons": [], "orgs": []}


def _score_sentiment(text: str) -> float:
    """Return VADER compound score in [-1, 1]."""
    return _sia.polarity_scores(text)["compound"]


def _build_context(articles: List[Dict]) -> str:
    """Flatten articles into a numbered context block for the LLM."""
    lines = []
    for i, a in enumerate(articles, 1):
        pub = a.get("published", "")[:16]
        lines.append(f"[{i}] ({pub}) {a['title']} — {a['summary'][:300]}")
    return "\n".join(lines)


# ── Main service function ─────────────────────────────────────────────────────
def build_story_arc(topic: str) -> Dict[str, Any]:
    """
    Full Story Arc pipeline.
    Returns a dict with: timeline, key_players, sentiment_data,
    contrarian_view, article_count. No future predictions.
    """
    articles = search_articles(topic, max_results=20)
    if not articles:
        return {"error": "No relevant articles found. Try a different topic."}

    # ── 1. Sentiment per article ───────────────────────────────────────────────
    sentiment_data = []
    for a in articles:
        text = a["title"] + " " + a["summary"]
        score = _score_sentiment(text)
        sentiment_data.append({
            "title": a["title"][:80],
            "score": round(score, 3),
            "published": a.get("published", ""),
            "link": a.get("link", ""),
        })

    # ── 2. Key players via spaCy NER ──────────────────────────────────────────
    combined_text = " ".join(
        a["title"] + " " + a["summary"] for a in articles
    )
    entities = _extract_entities_spacy(combined_text)

    # ── 3. Narrative arc via LLM ──────────────────────────────────────────────
    context = _build_context(articles[:12])
    prompt = f"""You are a business journalist AI. Based on the following Economic Times news articles about "{topic}", produce a structured story arc in pure JSON (no markdown fences).

NEWS ARTICLES:
{context}

Return this exact JSON structure:
{{
  "timeline": [
    {{"date": "YYYY-MM-DD or exact date from articles", "event": "one-sentence description of what happened", "significance": "high|medium|low"}}
  ],
  "key_players": [
    {{"name": "Person or Org name", "role": "their role in this story", "stance": "positive|negative|neutral"}}
  ],
  "sentiment_trend": "rising|falling|mixed|stable",
  "sentiment_summary": "2-sentence explanation of overall sentiment based strictly on what has been reported.",
  "contrarian_view": "A well-reasoned alternative perspective on this story based only on facts already reported (2-3 sentences). No speculation."
}}

Rules:
- timeline should have 4-8 events in strict chronological order using only dates mentioned in the articles
- key_players should have 3-6 entries mixing persons and organisations
- Do NOT speculate, predict, or invent future events — only use facts from the articles above
- Return ONLY the JSON object, no extra text"""

    client, model = get_llm_client()
    arc_data = {}
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=1500,
        )
        raw = resp.choices[0].message.content.strip()
        # Strip markdown fences if model added them anyway
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
        arc_data = json.loads(raw)
    except json.JSONDecodeError:
        arc_data = {
            "timeline": [],
            "key_players": [],
            "sentiment_trend": "mixed",
            "sentiment_summary": "Could not parse LLM response.",
            "contrarian_view": "Analysis unavailable.",
        }
    except Exception as e:
        arc_data = {
            "timeline": [],
            "key_players": [],
            "sentiment_trend": "mixed",
            "sentiment_summary": f"LLM error: {str(e)}",
            "contrarian_view": "LLM unavailable — is Ollama running?",
        }

    # Merge NER entities that might be missed by LLM
    existing_names = {p["name"].lower() for p in arc_data.get("key_players", [])}
    for person in entities.get("persons", []):
        if person.lower() not in existing_names:
            arc_data.setdefault("key_players", []).append(
                {"name": person, "role": "Key Person", "stance": "neutral"}
            )
            existing_names.add(person.lower())

    return {
        "topic": topic,
        "article_count": len(articles),
        "sentiment_data": sentiment_data,
        "timeline": arc_data.get("timeline", []),
        "key_players": arc_data.get("key_players", []),
        "sentiment_trend": arc_data.get("sentiment_trend", "mixed"),
        "sentiment_summary": arc_data.get("sentiment_summary", ""),
        "contrarian_view": arc_data.get("contrarian_view", ""),
    }
