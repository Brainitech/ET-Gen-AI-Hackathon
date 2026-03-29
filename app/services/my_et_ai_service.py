"""
My ET AI Service — Persona-Aware News Intelligence.

Generates:
  1. persona_snippet  — "What this means for you" (1-2 sentences, inline on card)
  2. deep_dive        — Full contextual breakdown (modal, 4 sections)

Both use get_llm_client() so they work with Groq or local Ollama —
zero new dependencies, zero new API keys.
"""

from __future__ import annotations

import json
import logging
import re
from datetime import datetime, timezone
from typing import Any

from app.core.config import get_llm_client
from app.services.rss_service import fetch_all_articles, search_articles

logger = logging.getLogger(__name__)


# ── Persona emoji map (used in prompts for tone calibration) ──────
_PERSONA_TONE = {
    "investor":  "a retail investor tracking Indian markets and MFs",
    "founder":   "a startup founder watching the funding ecosystem",
    "student":   "a student learning about business — explain jargon simply",
    "executive": "a senior corporate executive focused on strategy and industry impact",
}


# ================================================================
# 1. Persona Snippet — inline card insight
# ================================================================

def generate_persona_snippet(
    article_title: str,
    article_summary: str,
    persona_type: str,
    context_summary: str,
) -> str:
    """
    Generate a 1-2 sentence 'What this means for you' snippet.

    Args:
        article_title:   Title of the news article.
        article_summary: Short summary / RSS description.
        persona_type:    investor | founder | student | executive
        context_summary: Plain-English user context from ExtendedUserProfile.get_context_summary()

    Returns:
        A concise, persona-aware insight string.
    """
    tone = _PERSONA_TONE.get(persona_type, "a business professional")

    prompt = f"""You are a personal financial news analyst. Your reader is {tone}.

Their specific context:
{context_summary}

News article:
Title: {article_title}
Summary: {article_summary}

Write exactly 1-2 sentences explaining what THIS news means specifically for THIS reader.
- Be direct and concrete. No vague generalities.
- Reference their specific context where possible (their sector, stage, holdings, goals).
- Start with the impact, not background.
- Do NOT repeat the headline. Add new insight.
- No markdown, no bullet points. Plain sentences only.

Your response (1-2 sentences only):"""

    client, model = get_llm_client()
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            max_tokens=120,
        )
        snippet = resp.choices[0].message.content.strip()
        # Clean up any accidental markdown
        snippet = re.sub(r"[*_`#]", "", snippet)
        return snippet
    except Exception as exc:
        logger.warning("Snippet generation failed: %s", exc)
        return "AI insight unavailable — click Deep Dive for analysis."


# ================================================================
# 2. Bulk Snippet Generation — top N articles
# ================================================================

def enrich_articles(
    articles: list[dict[str, Any]],
    persona_type: str,
    context_summary: str,
    top_n: int = 5,
) -> list[dict[str, Any]]:
    """
    Add persona_snippet to the top N articles.
    The rest are returned with snippet_ready=False for lazy loading.

    Args:
        articles:        Raw article dicts from rss_service.
        persona_type:    User's persona type string.
        context_summary: User's context for prompt injection.
        top_n:           How many to auto-enrich immediately.

    Returns:
        List of article dicts with added AI fields.
    """
    enriched = []
    for i, art in enumerate(articles):
        if i < top_n:
            snippet = generate_persona_snippet(
                article_title=art.get("title", ""),
                article_summary=art.get("summary", ""),
                persona_type=persona_type,
                context_summary=context_summary,
            )
            art["persona_snippet"] = snippet
            art["snippet_ready"] = True
        else:
            art["persona_snippet"] = ""
            art["snippet_ready"] = False

        art["sentiment"] = _quick_sentiment(art.get("title", "") + " " + art.get("summary", ""))
        art["tags"] = _extract_tags(art.get("title", "") + " " + art.get("summary", ""))
        enriched.append(art)

    return enriched


# ================================================================
# 3. Deep Dive — full contextual breakdown
# ================================================================

_DEEP_DIVE_SECTIONS = {
    "investor": [
        "Market & Portfolio Impact",
        "Sectors & Stocks Affected",
        "Risk Factors to Watch",
        "Action Points for Investors",
    ],
    "founder": [
        "What Changed in the Ecosystem",
        "Funding & Valuation Implications",
        "Competitor & Market Moves",
        "What Founders Should Do Now",
    ],
    "student": [
        "What Happened (Plain English)",
        "Why It Matters for India",
        "Key Terms Explained",
        "How This Connects to Your Studies",
    ],
    "executive": [
        "Strategic Implications",
        "Industry & Supply Chain Impact",
        "Regulatory & Policy Angle",
        "Leadership Action Points",
    ],
}


def generate_deep_dive(
    article_title: str,
    article_summary: str,
    persona_type: str,
    context_summary: str,
) -> dict[str, Any]:
    """
    Generate a full contextual breakdown of one article for a persona.

    Returns a dict with:
      - sections: list of {heading, content}
      - bottom_line: single most important takeaway
    """
    tone = _PERSONA_TONE.get(persona_type, "a business professional")
    sections = _DEEP_DIVE_SECTIONS.get(
        persona_type,
        ["Overview", "Key Implications", "Risks", "What to Do Next"],
    )
    sections_str = "\n".join(f"{i+1}. {s}" for i, s in enumerate(sections))

    prompt = f"""You are a senior business analyst writing for {tone}.

Their context:
{context_summary}

Article:
Title: {article_title}
Summary: {article_summary}

Write a deep contextual analysis with EXACTLY these 4 sections:
{sections_str}

Also write a "Bottom Line" — one punchy sentence: the single most important takeaway for this reader.

Respond in this exact JSON format (no markdown fences):
{{
  "sections": [
    {{"heading": "section name", "content": "2-3 sentences of insight"}},
    {{"heading": "section name", "content": "2-3 sentences of insight"}},
    {{"heading": "section name", "content": "2-3 sentences of insight"}},
    {{"heading": "section name", "content": "2-3 sentences of insight"}}
  ],
  "bottom_line": "One sentence takeaway."
}}

Rules:
- Each section content: 2-3 sentences, specific to this persona's context
- No generic commentary — make it actionable and relevant
- Return ONLY the JSON, no extra text"""

    client, model = get_llm_client()
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=800,
        )
        raw = resp.choices[0].message.content.strip()
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
        parsed = json.loads(raw)
        return {
            "sections": parsed.get("sections", []),
            "bottom_line": parsed.get("bottom_line", ""),
        }
    except Exception as exc:
        logger.warning("Deep dive generation failed: %s", exc)
        # Graceful fallback
        return {
            "sections": [
                {"heading": s, "content": "Analysis unavailable — LLM error."}
                for s in sections
            ],
            "bottom_line": "Could not generate analysis. Please try again.",
        }


# ================================================================
# 4. Feed Builder — full pipeline
# ================================================================

def build_personalized_briefing(
    user_id: str,
    persona_type: str,
    interests: list[str],
    context_summary: str,
    top_n_enriched: int = 5,
) -> dict[str, Any]:
    """
    Full pipeline:
      1. Fetch articles from ET RSS
      2. Filter by user interests
      3. Enrich top N with AI snippets
      4. Return structured briefing

    Args:
        user_id:          User identifier.
        persona_type:     investor | founder | student | executive
        interests:        List of interest keywords for article filtering.
        context_summary:  User's context string for LLM prompts.
        top_n_enriched:   How many articles get auto-generated snippets.

    Returns:
        Briefing dict ready for the API response.
    """
    # Step 1: Fetch relevant articles
    query = " ".join(interests) if interests else persona_type
    articles = search_articles(query, max_results=20)

    if not articles:
        articles = fetch_all_articles()[:20]

    # Step 2: Enrich top N
    enriched = enrich_articles(
        articles=articles,
        persona_type=persona_type,
        context_summary=context_summary,
        top_n=top_n_enriched,
    )

    enriched_count = sum(1 for a in enriched if a.get("snippet_ready"))

    return {
        "user_id": user_id,
        "persona_type": persona_type,
        "articles": enriched,
        "total_articles": len(enriched),
        "enriched_count": enriched_count,
        "generated_at": datetime.now(tz=timezone.utc).isoformat(),
    }


# ================================================================
# 5. Helpers — sentiment & tags (no LLM, instant)
# ================================================================

_POSITIVE_WORDS = {
    "surge", "gain", "rally", "growth", "profit", "rise", "boost",
    "record", "strong", "beat", "upgrade", "win", "expand", "launch",
    "invest", "fund", "unicorn", "ipo", "deal", "acquire",
}
_NEGATIVE_WORDS = {
    "fall", "drop", "crash", "loss", "decline", "cut", "layoff",
    "fraud", "penalty", "fine", "default", "debt", "crisis", "warn",
    "miss", "downgrade", "sell-off", "volatile", "risk", "probe",
}

_TAG_MAP = {
    "markets":   ["sensex", "nifty", "bse", "nse", "stock", "equity", "ipo", "sebi"],
    "startup":   ["startup", "funding", "series", "unicorn", "venture", "founder"],
    "policy":    ["rbi", "government", "budget", "regulation", "ministry", "parliament"],
    "macro":     ["gdp", "inflation", "interest rate", "fiscal", "economy", "recession"],
    "tech":      ["ai", "saas", "software", "platform", "cloud", "digital", "cyber"],
    "banking":   ["bank", "nbfc", "credit", "loan", "npa", "deposit", "repo"],
    "fmcg":      ["fmcg", "consumer", "retail", "brand", "sales"],
    "energy":    ["oil", "gas", "solar", "renewable", "power", "energy"],
}


def _quick_sentiment(text: str) -> str:
    lower = text.lower()
    pos = sum(1 for w in _POSITIVE_WORDS if w in lower)
    neg = sum(1 for w in _NEGATIVE_WORDS if w in lower)
    if pos > neg:
        return "positive"
    elif neg > pos:
        return "negative"
    return "neutral"


def _extract_tags(text: str) -> list[str]:
    lower = text.lower()
    return [tag for tag, keywords in _TAG_MAP.items() if any(kw in lower for kw in keywords)]
