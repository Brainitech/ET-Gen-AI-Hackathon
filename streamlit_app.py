"""
ET_Intelligence — Unified Streamlit Frontend
ET Hackathon Round 2 | All features in one app
My ET · Story Arc Tracker · News Summarizer · Vernacular Engine
"""

import re as _re
import streamlit as st
import requests
import plotly.graph_objects as go
import pandas as pd
import uuid

# ── Page Configuration ─────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ET_Intelligence — AI-Native Business News",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded",
)

API_BASE = "http://localhost:8000/api/v1"

# ── Global CSS — ET Dark Red Theme ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;800&family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: #0d0d0d; color: #e8e0d5; }

section[data-testid="stSidebar"] {
    background: #0a0a0a;
    border-right: 1px solid #1e1e1e;
}
section[data-testid="stSidebar"] .stRadio label {
    color: #888; font-size: 0.9rem; transition: color 0.2s;
}
section[data-testid="stSidebar"] .stRadio label:hover { color: #e8e0d5; }

.et-header {
    background: linear-gradient(135deg, #8B0000 0%, #B22222 50%, #8B0000 100%);
    padding: 0.75rem 2rem;
    display: flex; align-items: center; justify-content: space-between;
    border-bottom: 3px solid #FF4444;
    margin: -1rem -1rem 2rem -1rem;
}
.et-logo {
    font-family: 'Playfair Display', serif;
    font-size: 1.8rem; font-weight: 800; color: #FFFFFF; letter-spacing: -0.02em;
}
.et-logo span { color: #FFD700; }
.et-tagline {
    color: rgba(255,255,255,0.75); font-size: 0.78rem;
    font-weight: 500; letter-spacing: 0.15em; text-transform: uppercase;
}

.hero-banner {
    background: linear-gradient(135deg, rgba(139,0,0,0.25) 0%, rgba(178,34,34,0.12) 50%, rgba(139,0,0,0.2) 100%);
    border: 1px solid rgba(178,34,34,0.4); border-left: 5px solid #B22222;
    border-radius: 16px; padding: 2rem 2.5rem; margin-bottom: 2rem;
    position: relative; overflow: hidden;
}
.hero-banner::before {
    content: ''; position: absolute; top: -60px; right: -60px;
    width: 200px; height: 200px;
    background: radial-gradient(circle, rgba(178,34,34,0.15) 0%, transparent 70%);
    pointer-events: none;
}
.hero-title {
    font-family: 'Playfair Display', serif;
    font-size: 2.4rem; font-weight: 800; color: #FFFFFF; margin: 0; line-height: 1.1;
}
.hero-sub { color: #999; font-size: 1rem; margin-top: 0.6rem; }

.glass-card {
    background: #141414; border: 1px solid #252525; border-radius: 14px;
    padding: 1.5rem; margin-bottom: 1rem;
    transition: border-color 0.25s, box-shadow 0.25s, transform 0.15s;
}
.glass-card:hover {
    border-color: rgba(178,34,34,0.5);
    box-shadow: 0 4px 24px rgba(139,0,0,0.12), 0 1px 4px rgba(0,0,0,0.4);
    transform: translateY(-1px);
}

.section-heading {
    display: flex; align-items: center; gap: 0.6rem;
    font-size: 0.78rem; font-weight: 700; color: #e8e0d5;
    text-transform: uppercase; letter-spacing: 0.18em;
    margin: 2rem 0 1rem; padding: 0.6rem 1rem;
    background: linear-gradient(90deg, rgba(139,0,0,0.2) 0%, rgba(139,0,0,0.05) 100%);
    border-left: 3px solid #B22222; border-radius: 0 8px 8px 0;
}
.section-label {
    font-size: 0.72rem; font-weight: 700; color: #555;
    text-transform: uppercase; letter-spacing: 0.15em;
    margin-bottom: 1rem; padding-bottom: 0.5rem; border-bottom: 1px solid #1e1e1e;
}

.badge { display: inline-block; padding: 0.25rem 0.75rem; border-radius: 999px; font-size: 0.78rem; font-weight: 600; letter-spacing: 0.05em; text-transform: uppercase; }
.badge-positive { background: rgba(34,197,94,0.12); color: #4ade80; border: 1px solid rgba(34,197,94,0.25); }
.badge-negative { background: rgba(239,68,68,0.12); color: #f87171; border: 1px solid rgba(239,68,68,0.25); }
.badge-neutral  { background: rgba(148,163,184,0.12); color: #888; border: 1px solid rgba(148,163,184,0.2); }
.badge-rising   { background: rgba(34,197,94,0.12); color: #4ade80; border: 1px solid rgba(34,197,94,0.25); }
.badge-falling  { background: rgba(239,68,68,0.12); color: #f87171; border: 1px solid rgba(239,68,68,0.25); }
.badge-mixed    { background: rgba(251,191,36,0.12); color: #fbbf24; border: 1px solid rgba(251,191,36,0.25); }
.badge-stable   { background: rgba(139,0,0,0.15); color: #B22222; border: 1px solid rgba(178,34,34,0.3); }

.timeline-item { display: flex; gap: 1rem; margin-bottom: 0.75rem; align-items: flex-start; }
.timeline-dot { width: 10px; height: 10px; border-radius: 50%; background: #B22222; margin-top: 5px; flex-shrink: 0; box-shadow: 0 0 8px rgba(178,34,34,0.5); }
.timeline-dot-high   { background: #f87171; box-shadow: 0 0 8px rgba(248,113,113,0.5); }
.timeline-dot-medium { background: #fbbf24; box-shadow: 0 0 8px rgba(251,191,36,0.5); }
.timeline-dot-low    { background: #4ade80; box-shadow: 0 0 8px rgba(74,222,128,0.5); }

.player-card { background: rgba(139,0,0,0.05); border: 1px solid rgba(178,34,34,0.2); border-radius: 10px; padding: 0.75rem 1rem; margin-bottom: 0.5rem; }
.player-name { font-weight: 600; color: #e8e0d5; font-size: 0.95rem; }
.player-role { color: #666; font-size: 0.82rem; margin-top: 2px; }

.takeaway { display: flex; align-items: flex-start; gap: 0.75rem; padding: 0.6rem 0; border-bottom: 1px solid #1e1e1e; }
.takeaway:last-child { border-bottom: none; }
.takeaway-bullet { color: #B22222; font-weight: 700; font-size: 1rem; flex-shrink: 0; }
.takeaway-text { color: #ccc; font-size: 0.9rem; line-height: 1.5; }

.gloss-card { background: rgba(139,0,0,0.05); border: 1px solid rgba(178,34,34,0.2); border-radius: 10px; padding: 0.75rem 1rem; margin-bottom: 0.5rem; }
.gloss-term { font-weight: 600; color: #B22222; font-size: 0.9rem; }
.gloss-trans { color: #e8e0d5; font-size: 0.9rem; }
.gloss-exp { color: #666; font-size: 0.82rem; margin-top: 4px; }

.persona-card { background: #1a1a1a; border: 2px solid #2a2a2a; border-radius: 14px; padding: 1.5rem; cursor: pointer; transition: all 0.2s; text-align: center; }
.persona-card:hover { border-color: #8B0000; }
.persona-card.selected { border-color: #B22222; background: rgba(139,0,0,0.12); box-shadow: 0 0 20px rgba(178,34,34,0.2); }
.persona-icon { font-size: 2.2rem; margin-bottom: 0.5rem; }
.persona-name { font-weight: 700; font-size: 1rem; color: #fff; margin-bottom: 0.25rem; }
.persona-desc { color: #666; font-size: 0.8rem; line-height: 1.5; }

.news-card { background: #141414; border: 1px solid #252525; border-left: 4px solid #8B0000; border-radius: 12px; padding: 1.25rem 1.5rem; margin-bottom: 1rem; transition: border-color 0.2s, box-shadow 0.2s, transform 0.15s; }
.news-card:hover { border-left-color: #FF4444; box-shadow: 0 4px 24px rgba(139,0,0,0.18), inset 0 0 0 1px rgba(178,34,34,0.1); transform: translateX(2px); }
.news-meta { display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.5rem; }
.news-source { font-size: 0.72rem; font-weight: 700; color: #B22222; text-transform: uppercase; letter-spacing: 0.1em; }
.news-time { color: #555; font-size: 0.72rem; }
.news-title { font-size: 1.05rem; font-weight: 600; color: #e8e0d5; line-height: 1.4; margin-bottom: 0.5rem; }
.news-summary { color: #666; font-size: 0.85rem; line-height: 1.6; margin-bottom: 0.75rem; }

/* Home feed card */
.home-news-card {
    background: #111; border: 1px solid #1e1e1e; border-left: 3px solid #8B0000;
    border-radius: 10px; padding: 1rem 1.25rem; margin-bottom: 0.65rem;
    transition: border-color 0.2s, background 0.2s;
}
.home-news-card:hover { border-left-color: #FF4444; background: #161616; }
.home-cat-pill {
    display: inline-block; background: rgba(139,0,0,0.18);
    border: 1px solid rgba(178,34,34,0.3); color: #B22222;
    font-size: 0.65rem; font-weight: 700; padding: 2px 8px;
    border-radius: 999px; text-transform: uppercase; letter-spacing: 0.08em; margin-right: 0.4rem;
}
.home-news-title { font-size: 0.97rem; font-weight: 600; color: #e8e0d5; line-height: 1.4; margin: 0.35rem 0 0.4rem; }
.home-news-summary { color: #5a5a5a; font-size: 0.82rem; line-height: 1.55; }
.home-news-time { color: #444; font-size: 0.7rem; }

.ai-snippet { background: linear-gradient(135deg, rgba(139,0,0,0.12) 0%, rgba(139,0,0,0.06) 100%); border: 1px solid rgba(178,34,34,0.35); border-left: 3px solid #B22222; border-radius: 8px; padding: 0.85rem 1rem; margin-top: 0.85rem; }
.ai-snippet-label { font-size: 0.65rem; font-weight: 700; color: #B22222; text-transform: uppercase; letter-spacing: 0.14em; margin-bottom: 0.35rem; display: flex; align-items: center; gap: 4px; }
.ai-snippet-text { color: #d4ccc4; font-size: 0.9rem; line-height: 1.65; font-style: italic; }

.tag { display: inline-block; background: #1e1e1e; border: 1px solid #2a2a2a; color: #888; font-size: 0.7rem; font-weight: 500; padding: 0.2rem 0.6rem; border-radius: 999px; margin-right: 0.35rem; text-transform: uppercase; letter-spacing: 0.06em; }

.dot-positive { color: #4ade80; }
.dot-negative { color: #f87171; }
.dot-neutral  { color: #888; }

.deep-dive-section { background: #1a1a1a; border: 1px solid #2a2a2a; border-radius: 10px; padding: 1rem 1.25rem; margin-bottom: 0.75rem; }
.deep-dive-heading { font-size: 0.8rem; font-weight: 700; color: #B22222; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.4rem; }
.deep-dive-content { color: #ccc; font-size: 0.9rem; line-height: 1.7; }
.bottom-line { background: linear-gradient(135deg, rgba(139,0,0,0.2), rgba(178,34,34,0.1)); border: 1px solid rgba(178,34,34,0.4); border-radius: 10px; padding: 1rem 1.25rem; margin-top: 1rem; }
.bottom-line-label { font-size: 0.72rem; font-weight: 700; color: #FFD700; text-transform: uppercase; letter-spacing: 0.12em; margin-bottom: 0.3rem; }
.bottom-line-text { color: #fff; font-size: 0.95rem; font-weight: 500; line-height: 1.5; }

.err-box { background: rgba(239,68,68,0.1); border: 1px solid rgba(239,68,68,0.3); border-radius: 10px; padding: 1rem; color: #fca5a5; }
.info-box { background: rgba(139,0,0,0.07); border: 1px solid rgba(178,34,34,0.2); border-radius: 10px; padding: 1rem; color: #ccc; }

.stButton>button { background: linear-gradient(135deg, #8B0000, #B22222) !important; color: white !important; border: none !important; border-radius: 8px !important; font-weight: 600 !important; font-family: 'Inter', sans-serif !important; transition: opacity 0.2s !important; }
.stButton>button:hover { opacity: 0.85 !important; }

.stTextInput input, .stTextArea textarea, .stSelectbox select, .stMultiSelect [data-baseweb] { background: #1a1a1a !important; border-color: #2a2a2a !important; color: #e8e0d5 !important; border-radius: 8px !important; }
div[data-testid="stRadio"] label { color: #aaa !important; }
.stSpinner { color: #B22222 !important; }
.stMetric { background: linear-gradient(135deg, #1a1a1a 0%, #141414 100%); border: 1px solid #252525; border-top: 2px solid #8B0000; border-radius: 12px; padding: 1rem 1.25rem; }
section[data-testid="stSidebar"] details { border: 1px solid #1e1e1e !important; border-radius: 8px !important; background: #111 !important; }
section[data-testid="stSidebar"] details summary { color: #666 !important; font-size: 0.8rem !important; font-weight: 600 !important; padding: 0.5rem 0 !important; }
</style>
""", unsafe_allow_html=True)


# ── Shared Helpers ─────────────────────────────────────────────────────────────

def api_post(endpoint: str, payload: dict):
    try:
        r = requests.post(f"{API_BASE}{endpoint}", json=payload, timeout=300)
        r.raise_for_status()
        return r.json(), None
    except requests.exceptions.ConnectionError:
        return None, "❌ Cannot reach the backend. Run `uvicorn app.main:app --reload` first."
    except requests.exceptions.HTTPError as e:
        try:
            detail = e.response.json().get("detail", str(e))
        except Exception:
            detail = str(e)
        return None, f"API Error: {detail}"
    except Exception as e:
        return None, str(e)


def api_get(endpoint: str, params: dict = None):
    try:
        r = requests.get(f"{API_BASE}{endpoint}", params=params, timeout=120)
        r.raise_for_status()
        return r.json(), None
    except requests.exceptions.ConnectionError:
        return None, "❌ Cannot reach backend."
    except Exception as e:
        return None, str(e)


def sentiment_badge(score: float) -> str:
    if score >= 0.05:
        return '<span class="badge badge-positive">● Positive</span>'
    elif score <= -0.05:
        return '<span class="badge badge-negative">● Negative</span>'
    return '<span class="badge badge-neutral">● Neutral</span>'


def trend_badge(trend: str) -> str:
    cls = f"badge badge-{trend.lower()}" if trend.lower() in ["rising", "falling", "mixed", "stable"] else "badge badge-neutral"
    icons = {"rising": "↑", "falling": "↓", "mixed": "⟳", "stable": "→"}
    icon = icons.get(trend.lower(), "•")
    return f'<span class="{cls}">{icon} {trend.capitalize()}</span>'


def sentiment_dot(sentiment: str) -> str:
    if sentiment == "positive":
        return '<span class="dot-positive">▲</span>'
    elif sentiment == "negative":
        return '<span class="dot-negative">▼</span>'
    return '<span class="dot-neutral">●</span>'


def render_tags(tags: list) -> str:
    return "".join(f'<span class="tag">{t}</span>' for t in tags[:4])


# ── Client-side category detection (no LLM) ───────────────────────────────────
_CAT_KEYWORDS = {
    "Markets":  ["sensex", "nifty", "stock", "bse", "nse", "equity", "ipo", "sebi", "share"],
    "Startup":  ["startup", "funding", "series", "unicorn", "venture", "founder", "seed"],
    "Policy":   ["rbi", "government", "budget", "regulation", "ministry", "parliament"],
    "Macro":    ["gdp", "inflation", "interest rate", "fiscal", "economy", "recession"],
    "Tech":     ["ai", "software", "platform", "saas", "digital", "cloud", "cyber"],
    "Banking":  ["bank", "nbfc", "credit", "loan", "npa", "deposit", "repo"],
    "Energy":   ["oil", "gas", "solar", "renewable", "power", "energy"],
}

def _detect_category_client(title: str, summary: str) -> str:
    text = (title + " " + summary).lower()
    for cat, kws in _CAT_KEYWORDS.items():
        if any(kw in text for kw in kws):
            return cat
    return "General"


# ── Session State Init ─────────────────────────────────────────────────────────
defaults = {
    "my_et_page": "onboarding",
    "user_id": str(uuid.uuid4()),
    "profile": {},
    "persona": None,
    "briefing": None,
    "deep_dive_article": None,
    "vern_article_text": "",
    "vern_article_title": "",
    "vern_search_results": [],
    "home_articles": None,
    "home_category_filter": "All",
    "prefill_story_arc": "",
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding: 1.25rem 0 1rem; text-align:center; border-bottom: 1px solid #1a1a1a; margin-bottom: 1rem;">
        <div style="font-family:'Playfair Display',serif; font-size:2rem; font-weight:800; color:#FFFFFF; letter-spacing:-0.02em; line-height:1;">
            <span style="color:#B22222;">ET_Intelligence</span>
        </div>
        <div style="margin-top:6px;">
            <span style="background:rgba(139,0,0,0.2); border:1px solid rgba(178,34,34,0.4); color:#B22222; font-size:0.65rem; font-weight:700; letter-spacing:0.12em; text-transform:uppercase; padding:2px 10px; border-radius:999px;">ET Hackathon · Round 2</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "Navigate",
        ["🏠 Home", "📰 My ET — Newsroom", "📖 Story Arc Tracker", "📄 News Summarizer", "🌐 Vernacular Engine"],
        label_visibility="collapsed",
    )

    st.markdown("---")
    with st.expander("⚙️ Setup & Requirements", expanded=False):
        st.markdown("""
        <div style="font-size:0.8rem; line-height:2; color:#888;">
            <div><span style="color:#4ade80;">✓</span> <span style="color:#aaa;"> Ollama running locally</span></div>
            <div><span style="color:#4ade80;">✓</span> <code style="color:#B22222; background:rgba(139,0,0,0.15); padding:1px 6px; border-radius:4px; font-size:0.78rem;">llama3.1:8b</code> <span style="color:#aaa;"> pulled</span></div>
            <div style="margin-bottom:0.75rem;"><span style="color:#4ade80;">✓</span> <span style="color:#aaa;"> Backend on port 8000</span></div>
            <div style="border-top:1px solid #1e1e1e; padding-top:0.75rem; color:#555; font-size:0.75rem;">
                <div style="margin-bottom:4px;">Start Ollama:</div>
                <code style="color:#B22222; background:rgba(139,0,0,0.12); padding:3px 8px; border-radius:4px; font-size:0.72rem; display:block; margin-bottom:8px;">ollama run llama3.1:8b</code>
                <div style="margin-bottom:4px;">Start backend:</div>
                <code style="color:#B22222; background:rgba(139,0,0,0.12); padding:3px 8px; border-radius:4px; font-size:0.72rem; display:block;">uvicorn app.main:app --reload</code>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# HOME PAGE — Live ET General News Feed
# ═══════════════════════════════════════════════════════════════════════════════
if page == "🏠 Home":

    st.markdown("""
    <div class="et-header">
        <div class="et-logo"><span>ET_Intelligence</span></div>
        <div class="et-tagline">Live Economic Times · General News Feed</div>
    </div>
    """, unsafe_allow_html=True)

    col_title, col_refresh = st.columns([7, 1])
    with col_title:
        st.markdown("""
        <div style="margin-bottom: 0.25rem;">
            <span style="font-family:'Playfair Display',serif; font-size:1.8rem; font-weight:800; color:#fff;">
                Today's Business News
            </span>
        </div>
        <div style="color:#555; font-size:0.82rem;">
            Live from Economic Times RSS feeds · Markets · Tech · Startups · Economy · Policy
        </div>
        """, unsafe_allow_html=True)
    with col_refresh:
        st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)
        if st.button("↻ Refresh", use_container_width=True):
            st.session_state["home_articles"] = None
            st.rerun()

    st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

    # Fetch articles (cached per session, cleared on Refresh)
    if st.session_state["home_articles"] is None:
        with st.spinner("📡 Fetching live ET articles…"):
            data, err = api_get("/articles/feed", {"max_per_feed": 15})
        if err:
            st.markdown(f'<div class="err-box">{err}</div>', unsafe_allow_html=True)
            st.stop()
        articles_raw = data.get("articles", [])
        for art in articles_raw:
            art["_category"] = _detect_category_client(
                art.get("title", ""), art.get("summary", "")
            )
        st.session_state["home_articles"] = articles_raw

    articles_raw = st.session_state["home_articles"]
    categories_found = sorted(set(a["_category"] for a in articles_raw))
    sources_found    = sorted(set(a.get("source", "ET") for a in articles_raw))

    # Stats row
    m1, m2, m3, m4 = st.columns(4)
    with m1: st.metric("📰 Total Articles", len(articles_raw))
    with m2: st.metric("📡 Live Feeds", len(sources_found))
    with m3: st.metric("🗂️ Categories", len(categories_found))
    with m4: st.metric("🔄 Cache TTL", "5 min")

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    # Category filter
    all_cats = ["All"] + categories_found
    st.markdown('<div class="section-label">🗂️ Filter by Category</div>', unsafe_allow_html=True)
    cat_cols = st.columns(len(all_cats))
    for i, cat in enumerate(all_cats):
        with cat_cols[i]:
            is_active = st.session_state["home_category_filter"] == cat
            style = ("background:rgba(139,0,0,0.35); border:1px solid #B22222; color:#fff;"
                     if is_active else
                     "background:#1a1a1a; border:1px solid #2a2a2a; color:#666;")
            st.markdown(
                f'<div style="{style} text-align:center; padding:5px 0; border-radius:8px; '
                f'font-size:0.75rem; font-weight:600; text-transform:uppercase; letter-spacing:0.06em;">'
                f'{cat}</div>',
                unsafe_allow_html=True,
            )
            if st.button(cat, key=f"cat_{cat}", use_container_width=True):
                st.session_state["home_category_filter"] = cat
                st.rerun()

    st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

    # Apply filter
    active_cat = st.session_state["home_category_filter"]
    filtered = articles_raw if active_cat == "All" else [a for a in articles_raw if a.get("_category") == active_cat]

    st.markdown(
        f'<div style="color:#444; font-size:0.78rem; margin-bottom:1rem;">'
        f'Showing <b style="color:#B22222">{len(filtered)}</b> articles'
        f'{" in " + active_cat if active_cat != "All" else ""}'
        f'</div>',
        unsafe_allow_html=True,
    )

    if not filtered:
        st.markdown('<div class="info-box">No articles found for this category. Try refreshing.</div>', unsafe_allow_html=True)
    else:
        col_a, col_b = st.columns(2)
        for idx, art in enumerate(filtered):
            title   = art.get("title", "Untitled")
            summary = art.get("summary", "")
            source  = art.get("source", "ET")
            pub     = art.get("published", "")[:16]
            link    = art.get("link", "")
            cat     = art.get("_category", "General")

            # Strip any HTML tags that sneak in from RSS
            summary_clean = _re.sub(r"<[^>]+>", "", summary)[:200]

            card_html = f"""
            <div class="home-news-card">
                <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.2rem;">
                    <span class="home-cat-pill">{cat}</span>
                    <span class="home-news-time">{source} · {pub}</span>
                </div>
                <div class="home-news-title">{title}</div>
                <div class="home-news-summary">{summary_clean}{"…" if len(summary_clean) >= 200 else ""}</div>
            </div>
            """

            target_col = col_a if idx % 2 == 0 else col_b
            with target_col:
                st.markdown(card_html, unsafe_allow_html=True)
                btn_c1, btn_c2 = st.columns(2)
                with btn_c1:
                    if link:
                        st.markdown(
                            f'<a href="{link}" target="_blank" style="color:#B22222; font-size:0.78rem; text-decoration:none; font-weight:600;">Read on ET →</a>',
                            unsafe_allow_html=True,
                        )
                with btn_c2:
                    if st.button("🗺️ Story Arc", key=f"home_arc_{idx}", use_container_width=True):
                        topic_words = title.split()[:4]
                        st.session_state["prefill_story_arc"] = " ".join(topic_words)
                        st.rerun()
                st.markdown("<div style='height:0.25rem'></div>", unsafe_allow_html=True)

    # Feature strip
    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)
    st.markdown('<div class="section-label">⚡ AI Features — Use the sidebar to explore</div>', unsafe_allow_html=True)
    f1, f2, f3, f4 = st.columns(4)
    for col, icon, name, desc in zip(
        [f1, f2, f3, f4],
        ["📰", "🗺️", "📄", "🌐"],
        ["My ET", "Story Arc", "Summarizer", "Vernacular"],
        ["Persona-aware AI feed", "Topic visual narratives", "Article digest", "Hindi/Tamil/Telugu/Bengali"],
    ):
        with col:
            st.markdown(f"""
            <div style="background:#111; border:1px solid #1e1e1e; border-top:2px solid #8B0000;
                        border-radius:10px; padding:1rem; text-align:center;">
                <div style="font-size:1.6rem; margin-bottom:0.35rem;">{icon}</div>
                <div style="font-weight:700; color:#e8e0d5; font-size:0.88rem;">{name}</div>
                <div style="color:#444; font-size:0.75rem; margin-top:3px;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# MY ET — PERSONALIZED NEWSROOM
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "📰 My ET — Newsroom":

    st.markdown("""
    <div class="et-header">
        <div class="et-logo">My<span>ET</span></div>
        <div class="et-tagline">Your Personalized Newsroom · AI-Powered</div>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.my_et_page == "onboarding":

        st.markdown('<div style="max-width:640px; margin:0 auto; padding:2rem 0;">', unsafe_allow_html=True)
        st.markdown("""
        <div style="font-family:'Playfair Display',serif; font-size:2.2rem; font-weight:700; color:#FFFFFF; line-height:1.2; margin-bottom:0.5rem;">
            Who are you reading<br>the news as?
        </div>
        <div style="color:#888; font-size:0.95rem; margin-bottom:2rem;">
            Tell us your role. We'll make ET make sense for <em>your</em> world.
        </div>
        """, unsafe_allow_html=True)

        PERSONAS = {
            "investor":  {"icon": "📈", "name": "Investor",  "desc": "Track markets, MFs, stocks & portfolio impact"},
            "founder":   {"icon": "🚀", "name": "Founder",   "desc": "Funding news, competitor moves & ecosystem shifts"},
            "student":   {"icon": "🎓", "name": "Student",   "desc": "Plain-English explainers, career-relevant context"},
            "executive": {"icon": "🏢", "name": "Executive", "desc": "Strategy, industry trends & policy implications"},
        }

        cols = st.columns(4)
        for i, (key, meta) in enumerate(PERSONAS.items()):
            with cols[i]:
                selected = st.session_state.persona == key
                card_cls = "persona-card selected" if selected else "persona-card"
                st.markdown(f"""
                <div class="{card_cls}">
                    <div class="persona-icon">{meta['icon']}</div>
                    <div class="persona-name">{meta['name']}</div>
                    <div class="persona-desc">{meta['desc']}</div>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"Select {meta['name']}", key=f"persona_{key}", use_container_width=True):
                    st.session_state.persona = key
                    st.rerun()

        if st.session_state.persona:
            p = st.session_state.persona
            st.markdown("---")
            st.markdown(f"### Tell us more about you as a **{PERSONAS[p]['name']}**")

            profile_data = {"persona_type": p, "user_id": st.session_state.user_id, "name": ""}

            if p == "investor":
                name = st.text_input("Your name (optional)", placeholder="e.g. Ravi")
                sectors = st.multiselect("Sectors you invest in",
                    ["Banking", "IT", "Pharma", "Auto", "FMCG", "Real Estate", "Energy", "Metals", "Telecom"],
                    default=["Banking", "IT"])
                stocks = st.text_input("Stocks / MFs you track (comma separated)", placeholder="HDFC Bank, Nifty 50, Axis Bluechip Fund")
                col1, col2 = st.columns(2)
                with col1: style = st.selectbox("Investment style", ["long-term", "short-term", "swing-trader", "SIP"])
                with col2: risk = st.selectbox("Risk appetite", ["conservative", "moderate", "aggressive"])
                profile_data.update({
                    "name": name,
                    "interests": [s.lower() for s in sectors] + ["markets", "sensex", "stocks"],
                    "investor_context": {
                        "portfolio_sectors": [s.lower() for s in sectors],
                        "tracked_stocks": [s.strip() for s in stocks.split(",") if s.strip()],
                        "investment_style": style, "risk_appetite": risk,
                    },
                })

            elif p == "founder":
                name = st.text_input("Your name (optional)", placeholder="e.g. Priya")
                sector = st.text_input("Your startup sector", placeholder="e.g. Fintech, Edtech, D2C")
                col1, col2 = st.columns(2)
                with col1: stage = st.selectbox("Stage", ["idea", "early", "seed", "series-a", "series-b", "growth"])
                with col2: fundraising = st.selectbox("Fundraising status", ["not-raising", "actively-raising", "closing-round"])
                competitors = st.text_input("Competitors to watch (comma separated)", placeholder="e.g. Zepto, Blinkit, Swiggy Instamart")
                profile_data.update({
                    "name": name,
                    "interests": [sector.lower(), "startup", "funding", "venture capital", "ipo"],
                    "founder_context": {
                        "startup_sector": sector, "stage": stage,
                        "fundraising_status": fundraising,
                        "competitors": [c.strip() for c in competitors.split(",") if c.strip()],
                    },
                })

            elif p == "student":
                name = st.text_input("Your name (optional)", placeholder="e.g. Aryan")
                field = st.text_input("Field of study", placeholder="e.g. MBA Finance, B.Com, Engineering")
                goal = st.text_input("Career goal", placeholder="e.g. Investment Banking, Consulting, Product")
                level = st.selectbox("Business news knowledge", ["beginner", "intermediate", "advanced"])
                profile_data.update({
                    "name": name,
                    "interests": [field.lower(), goal.lower(), "economy", "business", "policy"],
                    "student_context": {"field_of_study": field, "career_goal": goal, "knowledge_level": level},
                })

            elif p == "executive":
                name = st.text_input("Your name (optional)", placeholder="e.g. Sunita")
                industry = st.text_input("Your industry", placeholder="e.g. FMCG, Manufacturing, Banking")
                function = st.selectbox("Your function", ["CEO/MD", "CFO", "CTO", "COO", "Strategy", "Operations", "Marketing", "HR"])
                size = st.selectbox("Company size", ["startup", "mid-size", "large", "enterprise"])
                focus = st.multiselect("Strategic priorities",
                    ["Expansion", "Cost optimisation", "Digital transformation", "Talent", "M&A", "Exports"],
                    default=["Expansion"])
                profile_data.update({
                    "name": name,
                    "interests": [industry.lower(), function.lower(), "policy", "corporate", "strategy"],
                    "executive_context": {
                        "industry": industry, "function": function, "company_size": size,
                        "strategic_focus": [f.lower() for f in focus],
                    },
                })

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🚀  Build My Newsroom", use_container_width=True):
                with st.spinner("Setting up your personalized newsroom…"):
                    data, err = api_post("/my-et/profile/extended", profile_data)
                    if err:
                        st.error(err)
                    else:
                        st.session_state.profile = profile_data
                        st.session_state.my_et_page = "feed"
                        st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    elif st.session_state.my_et_page == "feed":

        profile = st.session_state.profile
        persona = st.session_state.persona
        user_id = st.session_state.user_id

        PERSONA_META = {
            "investor":  {"icon": "📈", "name": "Investor"},
            "founder":   {"icon": "🚀", "name": "Founder"},
            "student":   {"icon": "🎓", "name": "Student"},
            "executive": {"icon": "🏢", "name": "Executive"},
        }

        col_greeting, col_refresh, col_switch = st.columns([5, 1, 1])
        with col_greeting:
            name = profile.get("name", "").strip()
            greeting = f"Good morning, {name}! 👋" if name else "Good morning! 👋"
            meta = PERSONA_META.get(persona, {})
            st.markdown(f"""
            <div>
                <div style="font-family:'Playfair Display',serif; font-size:1.6rem; font-weight:700; color:#fff; margin-bottom:0.2rem;">{greeting}</div>
                <div style="color:#666; font-size:0.85rem;">{meta.get('icon','')} Your <b style="color:#B22222">{meta.get('name','')} Newsroom</b> · Live from Economic Times</div>
            </div>
            """, unsafe_allow_html=True)
        with col_refresh:
            if st.button("↻ Refresh", use_container_width=True):
                st.session_state.briefing = None
                st.rerun()
        with col_switch:
            if st.button("← Switch", use_container_width=True):
                st.session_state.my_et_page = "onboarding"
                st.session_state.briefing = None
                st.session_state.persona = None
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-label">⚡ Switch Persona — Watch the same news transform</div>', unsafe_allow_html=True)
        switch_cols = st.columns(4)
        for i, (key, meta) in enumerate(PERSONA_META.items()):
            with switch_cols[i]:
                is_active = persona == key
                label = f"{meta['icon']} {meta['name']}"
                if is_active:
                    st.markdown(f'<div style="text-align:center; padding:0.5rem; background:rgba(139,0,0,0.3); border:1px solid #B22222; border-radius:8px; color:#fff; font-weight:600; font-size:0.85rem;">{label} ✓</div>', unsafe_allow_html=True)
                else:
                    if st.button(label, key=f"switch_{key}", use_container_width=True):
                        st.session_state.persona = key
                        new_profile = {"persona_type": key, "user_id": user_id, "interests": [key]}
                        api_post("/my-et/profile/extended", new_profile)
                        st.session_state.briefing = None
                        st.session_state.profile = new_profile
                        st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

        if st.session_state.briefing is None:
            with st.spinner("⚡ Fetching live ET news & generating your AI insights…"):
                data, err = api_get(f"/my-et/briefing/{user_id}", {"top_n": 5})
                if err:
                    st.error(err)
                    st.stop()
                st.session_state.briefing = data

        briefing = st.session_state.briefing
        articles = briefing.get("articles", [])

        m1, m2, m3, m4 = st.columns(4)
        with m1: st.metric("📰 Articles", briefing.get("total_articles", 0))
        with m2: st.metric("⚡ AI Insights", briefing.get("enriched_count", 0))
        with m3: st.metric("🎭 Persona", PERSONA_META.get(persona, {}).get("name", ""))
        with m4:
            positive = sum(1 for a in articles if a.get("sentiment") == "positive")
            st.metric("📊 Positive News", f"{positive}/{len(articles)}")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-label">📰 Your Feed</div>', unsafe_allow_html=True)

        if st.session_state.deep_dive_article:
            art = st.session_state.deep_dive_article
            with st.expander(f"🔍 Deep Dive: {art['title'][:60]}…", expanded=True):
                with st.spinner("Generating contextual analysis…"):
                    dd_data, dd_err = api_post("/my-et/deep-dive", {
                        "user_id": user_id,
                        "article_title": art["title"],
                        "article_summary": art["summary"],
                        "article_link": art.get("link", ""),
                    })
                if dd_err:
                    st.error(dd_err)
                elif dd_data:
                    dd_cols = st.columns(2)
                    for i, section in enumerate(dd_data.get("sections", [])):
                        with dd_cols[i % 2]:
                            st.markdown(f"""
                            <div class="deep-dive-section">
                                <div class="deep-dive-heading">{section.get('heading','')}</div>
                                <div class="deep-dive-content">{section.get('content','')}</div>
                            </div>
                            """, unsafe_allow_html=True)
                    if dd_data.get("bottom_line"):
                        st.markdown(f"""
                        <div class="bottom-line">
                            <div class="bottom-line-label">⚡ Bottom Line for You</div>
                            <div class="bottom-line-text">{dd_data['bottom_line']}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    if art.get("link"):
                        st.markdown(f'<br><a href="{art["link"]}" target="_blank" style="color:#B22222; font-size:0.85rem;">Read full article on ET →</a>', unsafe_allow_html=True)
                if st.button("✕ Close Deep Dive"):
                    st.session_state.deep_dive_article = None
                    st.rerun()
            st.markdown("<br>", unsafe_allow_html=True)

        for i, art in enumerate(articles):
            title     = art.get("title", "Untitled")
            summary   = art.get("summary", "")[:220]
            source    = art.get("source", "ET")
            pub       = art.get("published", "")[:16]
            snippet   = art.get("persona_snippet", "")
            ready     = art.get("snippet_ready", False)
            sentiment = art.get("sentiment", "neutral")
            tags      = art.get("tags", [])
            link      = art.get("link", "")

            st.markdown(f"""
            <div class="news-card">
                <div class="news-meta">
                    <span class="news-source">{source}</span>
                    <span class="news-time">{pub}</span>
                    {sentiment_dot(sentiment)}
                    <span style="font-size:0.72rem; color:#555;">{sentiment.capitalize()}</span>
                </div>
                <div class="news-title">{title}</div>
                <div class="news-summary">{summary}…</div>
                {render_tags(tags)}
                {"" if not snippet else f'''
<div class="ai-snippet">
                    <div class="ai-snippet-label">⚡ What this means for you</div>
                    <div class="ai-snippet-text">{snippet.replace("<", "&lt;").replace(">", "&gt;")}</div>
                </div>'''}
            </div>
            """, unsafe_allow_html=True)

            btn_col1, btn_col2, btn_col3 = st.columns([2, 2, 6])
            with btn_col1:
                if st.button("🔍 Deep Dive", key=f"dd_{i}", use_container_width=True):
                    st.session_state.deep_dive_article = art
                    st.rerun()
            with btn_col2:
                if not ready:
                    if st.button("⚡ Get Insight", key=f"snip_{i}", use_container_width=True):
                        with st.spinner("Generating…"):
                            snip_data, snip_err = api_post("/my-et/snippet", {
                                "user_id": user_id,
                                "article_title": title,
                                "article_summary": art.get("summary", ""),
                            })
                        if snip_data:
                            articles[i]["persona_snippet"] = snip_data.get("snippet", "")
                            articles[i]["snippet_ready"] = True
                            st.session_state.briefing["articles"] = articles
                            st.rerun()
                else:
                    if link:
                        st.markdown(f'<a href="{link}" target="_blank" style="color:#B22222; font-size:0.8rem; text-decoration:none;">Read on ET →</a>', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# STORY ARC TRACKER
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "📖 Story Arc Tracker":

    st.markdown("""
    <div class="et-header">
        <div class="et-logo">Story <span>Arc</span></div>
        <div class="et-tagline">Visual Business Narratives · AI-Powered</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="hero-banner">
        <p class="hero-title">🗺️ Story Arc Tracker</p>
        <p class="hero-sub">Enter any business topic. AI builds a complete visual narrative from live ET articles.</p>
    </div>
    """, unsafe_allow_html=True)

    # Consume pre-fill from Home quick-launch
    prefill = st.session_state.get("prefill_story_arc", "")
    if prefill:
        st.session_state["prefill_story_arc"] = ""

    col_inp, col_btn = st.columns([4, 1])
    with col_inp:
        topic = st.text_input(
            "Business topic", value=prefill,
            placeholder="e.g. Adani Group, Jio IPO, RBI rate cut, Zomato…",
            label_visibility="collapsed",
        )
    with col_btn:
        generate = st.button("⚡ Generate Arc", use_container_width=True)

    st.markdown("""
    <div style="color:#555; font-size:0.8rem; margin-top:-0.5rem; margin-bottom:1rem;">
        Try: &nbsp;
        <span style="color:#B22222;">Adani Group</span> &nbsp;·&nbsp;
        <span style="color:#B22222;">Reliance Jio IPO</span> &nbsp;·&nbsp;
        <span style="color:#B22222;">RBI rate cut</span> &nbsp;·&nbsp;
        <span style="color:#B22222;">Startups funding winter</span>
    </div>
    """, unsafe_allow_html=True)

    # Auto-fire if prefill came from Home
    if prefill and topic:
        generate = True

    if generate and topic.strip():
        with st.spinner(f"🔍 Analysing topic across ET articles…"):
            data, err = api_post("/story-arc", {"topic": topic})

        if err:
            st.markdown(f'<div class="err-box">{err}</div>', unsafe_allow_html=True)
        elif data:
            m1, m2, m3, m4 = st.columns(4)
            with m1: st.metric("📰 Articles Analysed", data.get("article_count", 0))
            with m2: st.metric("📡 Data Source", data.get("data_source_badge", ""))
            with m3:
                last_up = data.get("last_updated", "")
                st.metric("🕒 Last Updated", last_up[:16] if last_up else "Just now")
            with m4: st.metric("📊 Sentiment Trend", data.get("sentiment_trend", "mixed").capitalize())

            sentiment_data = data.get("sentiment_data", [])
            if sentiment_data:
                st.markdown('<div class="section-heading">📊 Sentiment Over Articles</div>', unsafe_allow_html=True)
                df = pd.DataFrame(sentiment_data)
                df["color"] = df["score"].apply(lambda s: "#4ade80" if s >= 0.05 else ("#f87171" if s <= -0.05 else "#888"))
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=list(range(len(df))), y=df["score"], marker_color=df["color"],
                    hovertemplate="<b>%{customdata}</b><br>Score: %{y:.3f}<extra></extra>",
                    customdata=df["title"],
                ))
                fig.add_hline(y=0, line_color="rgba(255,255,255,0.15)", line_dash="dash")
                fig.add_hrect(y0=0.05, y1=1, fillcolor="rgba(74,222,128,0.05)", line_width=0)
                fig.add_hrect(y0=-1, y1=-0.05, fillcolor="rgba(248,113,113,0.05)", line_width=0)
                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    xaxis=dict(showticklabels=False, gridcolor="rgba(255,255,255,0.04)"),
                    yaxis=dict(gridcolor="rgba(255,255,255,0.04)", tickfont=dict(color="#666"), range=[-1, 1]),
                    margin=dict(l=0, r=0, t=10, b=10), height=220,
                )
                st.plotly_chart(fig, use_container_width=True)

            col_l, col_r = st.columns([3, 2])
            with col_l:
                timeline = data.get("timeline", [])
                if timeline:
                    st.markdown('<div class="section-heading">📅 Event Timeline</div>', unsafe_allow_html=True)
                    for ev in timeline:
                        sig = ev.get("significance", "medium").lower()
                        st.markdown(f"""
                        <div class="timeline-item">
                            <div class="timeline-dot timeline-dot-{sig}"></div>
                            <div>
                                <div style="color:#555; font-size:0.75rem;">{ev.get('date','')}</div>
                                <div style="color:#e8e0d5; font-size:0.88rem; margin-top:2px;">{ev.get('event','')}</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                sum_text = data.get("sentiment_summary", "")
                if sum_text:
                    st.markdown('<div class="section-heading">💬 Sentiment Analysis</div>', unsafe_allow_html=True)
                    st.markdown(f"""
                    <div class="glass-card">
                        <div style="margin-bottom:0.5rem;">{trend_badge(data.get("sentiment_trend","mixed"))}</div>
                        <div style="color:#ccc; font-size:0.9rem; line-height:1.6;">{sum_text}</div>
                    </div>
                    """, unsafe_allow_html=True)

            with col_r:
                players = data.get("key_players", [])
                if players:
                    st.markdown('<div class="section-heading">👥 Key Players</div>', unsafe_allow_html=True)
                    for p in players[:6]:
                        stance = p.get("stance", "neutral").lower()
                        st.markdown(f"""
                        <div class="player-card">
                            <div class="player-name">{p.get('name','')}</div>
                            <div class="player-role">{p.get('role','')}</div>
                            <div style="margin-top:6px;">{sentiment_badge(0.1 if stance=='positive' else (-0.1 if stance=='negative' else 0))}</div>
                        </div>
                        """, unsafe_allow_html=True)

            contrarian = data.get("contrarian_view", "")
            if contrarian:
                st.markdown('<div class="section-heading">🔄 Contrarian View</div>', unsafe_allow_html=True)
                st.markdown(f"""
                <div class="glass-card" style="border-color:rgba(251,191,36,0.25);">
                    <div style="color:#fbbf24; font-size:0.85rem; font-weight:600; margin-bottom:0.5rem;">⚠️ Alternative Perspective</div>
                    <div style="color:#ccc; font-size:0.9rem; line-height:1.7;">{contrarian}</div>
                </div>
                """, unsafe_allow_html=True)

            predictions = data.get("predictions", "")
            if predictions:
                st.markdown('<div class="section-heading">🔮 Predictions & What to Watch</div>', unsafe_allow_html=True)
                st.markdown(f"""
                <div class="glass-card" style="border-color:rgba(178,34,34,0.3);">
                    <div style="color:#B22222; font-size:0.85rem; font-weight:600; margin-bottom:0.5rem;">✨ Future Outlook</div>
                    <div style="color:#ccc; font-size:0.9rem; line-height:1.7;">{predictions}</div>
                </div>
                """, unsafe_allow_html=True)

    elif generate and not topic.strip():
        st.warning("Please enter a topic to analyse.")


# ═══════════════════════════════════════════════════════════════════════════════
# NEWS SUMMARIZER
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "📄 News Summarizer":

    st.markdown("""
    <div class="et-header">
        <div class="et-logo">News <span>Summary</span></div>
        <div class="et-tagline">AI Article Digest · Instant Insights</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="hero-banner">
        <p class="hero-title">📄 News Summarizer</p>
        <p class="hero-sub">Paste any article or URL. Get a crisp AI summary with key takeaways.</p>
    </div>
    """, unsafe_allow_html=True)

    input_mode = st.radio("Input type", ["📝 Paste Text", "🔗 Article URL"], horizontal=True)
    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    article_text = None
    article_url  = None

    if input_mode == "📝 Paste Text":
        article_text = st.text_area("Article text", placeholder="Paste the full article text here…", height=260, label_visibility="collapsed")
    else:
        article_url = st.text_input("Article URL", placeholder="https://economictimes.indiatimes.com/...", label_visibility="collapsed")

    summarize_btn = st.button("📄 Summarize Article", use_container_width=False)

    if summarize_btn:
        payload = {}
        if article_text:   payload["text"] = article_text
        elif article_url:  payload["url"]  = article_url
        else:
            st.warning("Please paste text or enter a URL.")
            st.stop()

        with st.spinner("🤖 Generating summary…"):
            data, err = api_post("/summarize", payload)

        if err:
            st.markdown(f'<div class="err-box">{err}</div>', unsafe_allow_html=True)
        elif data:
            m1, m2, m3 = st.columns(3)
            with m1: st.metric("🏷️ Category", data.get("category", "general").capitalize())
            with m2: st.metric("⏱️ Read Time", f"{data.get('read_time_min', 1)} min")
            with m3: st.metric("📏 Article Length", f"{data.get('char_count',0):,} chars")

            st.markdown('<div class="section-heading">💡 AI Summary</div>', unsafe_allow_html=True)
            st.markdown(f"""
            <div class="glass-card" style="border-color:rgba(178,34,34,0.3);">
                <div style="color:#e8e0d5; font-size:1rem; line-height:1.8;">{data.get("summary", "Summary not available.")}</div>
            </div>
            """, unsafe_allow_html=True)

            takeaways = data.get("key_takeaways", [])
            if takeaways:
                st.markdown('<div class="section-heading">🎯 Key Takeaways</div>', unsafe_allow_html=True)
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                for i, t in enumerate(takeaways, 1):
                    st.markdown(f"""
                    <div class="takeaway">
                        <span class="takeaway-bullet">{i}.</span>
                        <span class="takeaway-text">{t}</span>
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

            impact = data.get("contextual_impact", "")
            if impact:
                st.markdown('<div class="section-heading">🌍 Contextual Impact</div>', unsafe_allow_html=True)
                st.markdown(f"""
                <div class="glass-card" style="border-color:rgba(178,34,34,0.2);">
                    <div style="color:#e8e0d5; font-size:0.95rem; line-height:1.7;">{impact}</div>
                </div>
                """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# VERNACULAR ENGINE
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "🌐 Vernacular Engine":

    st.markdown("""
    <div class="et-header">
        <div class="et-logo">Vernacular <span>Engine</span></div>
        <div class="et-tagline">Business News in Your Language</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="hero-banner">
        <p class="hero-title">🌐 Vernacular Engine</p>
        <p class="hero-sub">Search ET articles, enter a URL, or paste text — then translate with local cultural context.</p>
    </div>
    """, unsafe_allow_html=True)

    LANG_OPTIONS = {
        "🇮🇳 Hindi (हिंदी)": "hi",
        "🇮🇳 Tamil (தமிழ்)": "ta",
        "🇮🇳 Telugu (తెలుగు)": "te",
        "🇮🇳 Bengali (বাংলা)": "bn",
    }

    input_mode = st.radio(
        "How to find the article",
        ["🔍 Search ET Articles", "🔗 Article URL", "📝 Paste Text"],
        horizontal=True, label_visibility="collapsed",
    )
    st.markdown("<div style='height:0.25rem'></div>", unsafe_allow_html=True)

    if input_mode == "🔍 Search ET Articles":
        col_s, col_sb = st.columns([5, 1])
        with col_s:
            search_query = st.text_input("Search ET", placeholder="e.g. RBI rate cut, Infosys earnings, startup funding…", label_visibility="collapsed")
        with col_sb:
            do_search = st.button("🔍 Search", use_container_width=True)

        if do_search and search_query.strip():
            with st.spinner("Searching ET articles…"):
                try:
                    r = requests.get(f"{API_BASE}/articles/search", params={"q": search_query}, timeout=15)
                    r.raise_for_status()
                    st.session_state["vern_search_results"] = r.json().get("articles", [])
                    st.session_state["vern_article_text"] = ""
                    st.session_state["vern_article_title"] = ""
                except Exception as e:
                    st.markdown(f'<div class="err-box">Search failed: {e}</div>', unsafe_allow_html=True)

        results = st.session_state.get("vern_search_results", [])
        if results:
            st.markdown(f'<div style="color:#555; font-size:0.8rem; margin-bottom:0.75rem;">{len(results)} articles found — click → to load one</div>', unsafe_allow_html=True)
            for art in results:
                title   = art.get("title", "Untitled")
                summary = art.get("summary", "")[:160]
                pub     = art.get("published", "")[:16]
                link    = art.get("link", "")
                is_sel  = st.session_state.get("vern_article_title") == title
                border_col = "rgba(178,34,34,0.6)" if is_sel else "rgba(255,255,255,0.05)"
                bg_col     = "rgba(139,0,0,0.08)"  if is_sel else "rgba(255,255,255,0.02)"

                col_card, col_pick = st.columns([10, 1])
                with col_card:
                    st.markdown(f"""
                    <div class="glass-card" style="padding:0.85rem 1.1rem; border-color:{border_col}; background:{bg_col}; margin-bottom:0.4rem;">
                        <div style="font-weight:600; color:#e8e0d5; font-size:0.9rem;">{title}</div>
                        <div style="color:#555; font-size:0.75rem; margin-top:2px;">{pub}</div>
                        <div style="color:#666; font-size:0.82rem; margin-top:4px; line-height:1.5;">{summary}…</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col_pick:
                    btn_label = "✓" if is_sel else "→"
                    if st.button(btn_label, key=f"pick_{link}", use_container_width=True):
                        with st.spinner("Fetching full article…"):
                            try:
                                fr = requests.get(f"{API_BASE}/articles/fetch", params={"url": link}, timeout=20)
                                fr.raise_for_status()
                                fetched = fr.json().get("text", "")
                                st.session_state["vern_article_text"] = fetched if fetched else (art.get("title", "") + ". " + art.get("summary", ""))
                            except Exception:
                                st.session_state["vern_article_text"] = art.get("title", "") + ". " + art.get("summary", "")
                            st.session_state["vern_article_title"] = title
                        st.rerun()

        if st.session_state.get("vern_article_title"):
            st.markdown(f"""
            <div class="glass-card" style="border-color:rgba(178,34,34,0.4); margin-top:0.5rem; padding:0.85rem 1.1rem;">
                <div style="color:#B22222; font-size:0.78rem; font-weight:700; text-transform:uppercase; letter-spacing:0.08em;">✅ Selected Article</div>
                <div style="color:#e8e0d5; font-size:0.9rem; font-weight:500; margin-top:6px;">{st.session_state['vern_article_title']}</div>
                <div style="color:#555; font-size:0.78rem; margin-top:4px;">{len(st.session_state['vern_article_text']):,} characters loaded</div>
            </div>
            """, unsafe_allow_html=True)

    elif input_mode == "🔗 Article URL":
        col_u, col_ub = st.columns([5, 1])
        with col_u:
            article_url = st.text_input("ET Article URL", placeholder="https://economictimes.indiatimes.com/...", label_visibility="collapsed")
        with col_ub:
            fetch_btn = st.button("📥 Fetch", use_container_width=True)

        if fetch_btn and article_url.strip():
            with st.spinner("Fetching article…"):
                try:
                    fr = requests.get(f"{API_BASE}/articles/fetch", params={"url": article_url.strip()}, timeout=20)
                    fr.raise_for_status()
                    fd = fr.json()
                    fetched = fd.get("text", "")
                    if fetched:
                        st.session_state["vern_article_text"] = fetched
                        st.session_state["vern_article_title"] = article_url.strip()
                        st.success(f"✅ Fetched {fd.get('char_count', len(fetched)):,} characters")
                    else:
                        st.error("Could not extract text. Try the Paste Text mode.")
                except Exception as e:
                    st.error(f"Fetch failed: {e}")

        if st.session_state.get("vern_article_text"):
            with st.expander("📄 Preview fetched text", expanded=False):
                st.caption(st.session_state["vern_article_text"][:600] + "…")

    elif input_mode == "📝 Paste Text":
        pasted = st.text_area("Paste English business text", placeholder="Paste any English business news text here…", height=200, label_visibility="collapsed")
        if pasted.strip():
            st.session_state["vern_article_text"] = pasted.strip()
            st.session_state["vern_article_title"] = "Pasted text"

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    col_lang, col_mod, col_tbtn = st.columns([2, 2, 1])
    with col_lang:
        selected_lang_label = st.selectbox("Target language", list(LANG_OPTIONS.keys()))
        selected_lang_code  = LANG_OPTIONS[selected_lang_label]
    with col_mod:
        selected_model = st.selectbox("Translation Model", ["llama3.1:8b", "aya:8b", "gemma2:9b", "qwen2.5:7b", "mistral:7b"])
    with col_tbtn:
        st.markdown("<div style='height:1.75rem'></div>", unsafe_allow_html=True)
        translate_btn = st.button("🌐 Translate", use_container_width=True,
                                  disabled=not bool(st.session_state.get("vern_article_text")))

    if translate_btn and st.session_state.get("vern_article_text"):
        lang_display = selected_lang_label.split("(")[0].strip()
        with st.spinner(f"Translating to {lang_display} using {selected_model}…"):
            data, err = api_post("/translate", {
                "text":        st.session_state["vern_article_text"][:8000],
                "target_lang": selected_lang_code,
                "model":       selected_model,
            })

        if err:
            st.markdown(f'<div class="err-box">{err}</div>', unsafe_allow_html=True)
        elif data:
            st.markdown('<div class="section-heading">📄 Translation</div>', unsafe_allow_html=True)
            col_orig, col_trans = st.columns(2)
            with col_orig:
                st.markdown('<div style="color:#555; font-size:0.75rem; font-weight:700; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:0.5rem;">🇬🇧 Original (English)</div>', unsafe_allow_html=True)
                st.markdown(f"""
                <div class="glass-card" style="min-height:130px; max-height:320px; overflow-y:auto;">
                    <div style="color:#ccc; font-size:0.88rem; line-height:1.8;">{data.get('original','')[:1500]}</div>
                </div>
                """, unsafe_allow_html=True)
            with col_trans:
                native    = data.get("target_language_native", "")
                eng       = data.get("target_language", "")
                flag      = data.get("flag", "🇮🇳")
                model_used = data.get("model_used", "")
                st.markdown(f'<div style="color:#555; font-size:0.75rem; font-weight:700; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:0.5rem;">{flag} Translated ({eng} · {native}) / <span style="color:#B22222">{model_used}</span></div>', unsafe_allow_html=True)
                st.markdown(f"""
                <div class="glass-card" style="min-height:130px; max-height:320px; overflow-y:auto; border-color:rgba(178,34,34,0.3);">
                    <div style="color:#e8e0d5; font-size:0.95rem; line-height:1.9;">{data.get('improved_translation', data.get('base_translation',''))}</div>
                </div>
                """, unsafe_allow_html=True)

            context_note = data.get("local_context_note", "")
            if context_note:
                st.markdown('<div class="section-heading">📍 Local Context Note</div>', unsafe_allow_html=True)
                st.markdown(f"""
                <div class="glass-card" style="border-color:rgba(251,191,36,0.25);">
                    <div style="color:#fbbf24; font-size:0.8rem; font-weight:700; margin-bottom:0.5rem;">🗺️ FOR LOCAL READERS</div>
                    <div style="color:#ccc; font-size:0.9rem; line-height:1.7;">{context_note}</div>
                </div>
                """, unsafe_allow_html=True)

            glossary = data.get("terminology_glossary", [])
            if glossary:
                st.markdown('<div class="section-heading">📚 Business Terminology Glossary</div>', unsafe_allow_html=True)
                cols = st.columns(min(len(glossary), 3))
                for i, item in enumerate(glossary):
                    with cols[i % 3]:
                        st.markdown(f"""
                        <div class="gloss-card">
                            <div class="gloss-term">{item.get('term','')}</div>
                            <div class="gloss-trans">{item.get('translation','')}</div>
                            <div class="gloss-exp">{item.get('explanation','')}</div>
                        </div>
                        """, unsafe_allow_html=True)
