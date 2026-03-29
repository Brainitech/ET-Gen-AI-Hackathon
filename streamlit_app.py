"""
ET_Intelligence — Unified Streamlit Frontend (Revamped UI v2)
ET Hackathon Round 2 | My ET · Story Arc Tracker · News Summarizer · Vernacular Engine
"""

import re as _re
import streamlit as st
import requests
import plotly.graph_objects as go
import pandas as pd
import uuid

# ── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ET_Intelligence",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded",
)

API_BASE = "http://localhost:8000/api/v1"

# ── Session State Defaults ────────────────────────────────────────────────────
defaults = {
    "dark_mode": True,
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

# ── Theme CSS Injection ────────────────────────────────────────────────────────
IS_DARK = st.session_state.dark_mode

DARK_VARS = """
    --bg-0: #080808;
    --bg-1: #111111;
    --bg-2: #181818;
    --bg-3: #232323;
    --border: #2c2c2c;
    --border-accent: rgba(196,30,58,0.35);
    --text-1: #f0ebe4;
    --text-2: #8a8278;
    --text-3: #4a4a4a;
    --accent: #C41E3A;
    --accent-hover: #e02244;
    --accent-dim: rgba(196,30,58,0.10);
    --accent-glow: rgba(196,30,58,0.22);
    --positive: #4ade80;
    --positive-dim: rgba(74,222,128,0.10);
    --negative: #f87171;
    --negative-dim: rgba(248,113,113,0.10);
    --warning: #fbbf24;
    --warning-dim: rgba(251,191,36,0.10);
    --gold: #e0b84a;
    --sidebar-bg: #0c0c0c;
    --header-gradient: linear-gradient(135deg, #6a0000 0%, #9e1a1a 60%, #6a0000 100%);
    --card-shadow: 0 2px 10px rgba(0,0,0,0.45);
    --card-shadow-hover: 0 6px 24px rgba(0,0,0,0.55), 0 0 0 1px rgba(196,30,58,0.18);
    --input-bg: #1e1e1e;
    --metric-border-top: #C41E3A;
    --scrollbar-thumb: #333;
"""

LIGHT_VARS = """
    --bg-0: #f4f1ee;
    --bg-1: #ffffff;
    --bg-2: #faf8f6;
    --bg-3: #f0ece8;
    --border: #e4deda;
    --border-accent: rgba(196,30,58,0.22);
    --text-1: #1a1714;
    --text-2: #6b6360;
    --text-3: #aaa6a2;
    --accent: #b81c36;
    --accent-hover: #961630;
    --accent-dim: rgba(184,28,54,0.07);
    --accent-glow: rgba(184,28,54,0.14);
    --positive: #15803d;
    --positive-dim: rgba(21,128,61,0.08);
    --negative: #b91c1c;
    --negative-dim: rgba(185,28,28,0.08);
    --warning: #b45309;
    --warning-dim: rgba(180,83,9,0.08);
    --gold: #92660a;
    --sidebar-bg: #ede9e4;
    --header-gradient: linear-gradient(135deg, #8a0000 0%, #c41e3a 60%, #8a0000 100%);
    --card-shadow: 0 1px 6px rgba(0,0,0,0.07);
    --card-shadow-hover: 0 4px 18px rgba(0,0,0,0.11), 0 0 0 1px rgba(196,30,58,0.12);
    --input-bg: #f8f5f2;
    --metric-border-top: #b81c36;
    --scrollbar-thumb: #c8c2bc;
"""

COMMON_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;0,700;0,800;1,600&family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [class*="css"] {
    font-family: 'DM Sans', -apple-system, sans-serif;
    color: var(--text-1);
    -webkit-font-smoothing: antialiased;
}

.stApp { background: var(--bg-0) !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--scrollbar-thumb); border-radius: 99px; }
::-webkit-scrollbar-thumb:hover { background: var(--accent); }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: var(--sidebar-bg) !important;
    border-right: 1px solid var(--border) !important;
}
section[data-testid="stSidebar"] > div { padding-top: 0 !important; }
section[data-testid="stSidebar"] .stRadio label {
    color: var(--text-2) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.875rem !important;
    font-weight: 500 !important;
    padding: 0.3rem 0 !important;
    transition: color 0.18s;
}
section[data-testid="stSidebar"] .stRadio label:hover { color: var(--text-1) !important; }
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
    color: var(--text-2) !important;
    font-size: 0.8rem !important;
}

/* ── Header Bar ── */
.et-header {
    background: var(--header-gradient);
    padding: 0.9rem 2rem;
    display: flex; align-items: center; justify-content: space-between;
    border-bottom: 2px solid var(--accent);
    margin: -1rem -1rem 2rem -1rem;
}
.et-logo {
    font-family: 'Playfair Display', serif;
    font-size: 1.65rem; font-weight: 800; color: #fff; letter-spacing: -0.01em;
}
.et-logo span { color: var(--gold); }
.et-tagline {
    color: rgba(255,255,255,0.58); font-size: 0.68rem;
    font-weight: 600; letter-spacing: 0.2em; text-transform: uppercase;
}

/* ── Hero Banner ── */
.hero-banner {
    background: var(--accent-dim);
    border: 1px solid var(--border-accent);
    border-left: 4px solid var(--accent);
    border-radius: 12px; padding: 1.6rem 2rem; margin-bottom: 1.75rem;
}
.hero-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.85rem; font-weight: 800; color: var(--text-1);
    line-height: 1.15; margin: 0;
}
.hero-sub { color: var(--text-2); font-size: 0.9rem; margin-top: 0.45rem; line-height: 1.5; }

/* ── Section Heading ── */
.section-heading {
    display: flex; align-items: center; gap: 0.45rem;
    font-size: 0.68rem; font-weight: 700; color: var(--text-1);
    text-transform: uppercase; letter-spacing: 0.18em;
    margin: 1.75rem 0 0.9rem;
    padding: 0.45rem 0.85rem;
    background: var(--accent-dim); border-left: 3px solid var(--accent);
    border-radius: 0 6px 6px 0;
}
.section-label {
    font-size: 0.67rem; font-weight: 700; color: var(--text-3);
    text-transform: uppercase; letter-spacing: 0.16em;
    margin-bottom: 0.7rem; padding-bottom: 0.4rem; border-bottom: 1px solid var(--border);
}

/* ── Glass Card ── */
.glass-card {
    background: var(--bg-2); border: 1px solid var(--border);
    border-radius: 12px; padding: 1.2rem 1.4rem; margin-bottom: 0.9rem;
    box-shadow: var(--card-shadow);
    transition: border-color 0.2s, box-shadow 0.2s, transform 0.15s;
}
.glass-card:hover {
    border-color: var(--border-accent);
    box-shadow: var(--card-shadow-hover);
    transform: translateY(-1px);
}

/* ── Badges ── */
.badge {
    display: inline-flex; align-items: center; gap: 3px;
    padding: 0.18rem 0.6rem; border-radius: 999px;
    font-size: 0.68rem; font-weight: 700; letter-spacing: 0.04em; text-transform: uppercase;
}
.badge-positive { background: var(--positive-dim); color: var(--positive); border: 1px solid rgba(74,222,128,0.2); }
.badge-negative { background: var(--negative-dim); color: var(--negative); border: 1px solid rgba(248,113,113,0.2); }
.badge-neutral  { background: var(--bg-3); color: var(--text-2); border: 1px solid var(--border); }
.badge-rising   { background: var(--positive-dim); color: var(--positive); border: 1px solid rgba(74,222,128,0.2); }
.badge-falling  { background: var(--negative-dim); color: var(--negative); border: 1px solid rgba(248,113,113,0.2); }
.badge-mixed    { background: var(--warning-dim); color: var(--warning); border: 1px solid rgba(251,191,36,0.2); }
.badge-stable   { background: var(--accent-dim); color: var(--accent); border: 1px solid var(--border-accent); }

/* ── Timeline ── */
.timeline-item {
    display: flex; gap: 0.8rem; align-items: flex-start;
    padding: 0.7rem 1rem; margin-bottom: 0.6rem;
    background: var(--bg-2); border: 1px solid var(--border);
    border-radius: 10px; transition: border-color 0.18s;
}
.timeline-item:hover { border-color: var(--border-accent); }
.timeline-dot {
    width: 9px; height: 9px; border-radius: 50%;
    background: var(--accent); flex-shrink: 0; margin-top: 5px;
    box-shadow: 0 0 0 3px var(--accent-dim);
}
.timeline-dot-high   { background: var(--negative); box-shadow: 0 0 0 3px var(--negative-dim); }
.timeline-dot-medium { background: var(--warning); box-shadow: 0 0 0 3px var(--warning-dim); }
.timeline-dot-low    { background: var(--positive); box-shadow: 0 0 0 3px var(--positive-dim); }

/* ── Player Card ── */
.player-card {
    background: var(--accent-dim); border: 1px solid var(--border-accent);
    border-radius: 10px; padding: 0.7rem 0.95rem; margin-bottom: 0.5rem;
    transition: border-color 0.18s, background 0.18s;
}
.player-card:hover { border-color: var(--accent); }
.player-name { font-weight: 600; color: var(--text-1); font-size: 0.9rem; }
.player-role { color: var(--text-2); font-size: 0.78rem; margin-top: 2px; }

/* ── Takeaways ── */
.takeaway {
    display: flex; align-items: flex-start; gap: 0.7rem;
    padding: 0.6rem 0; border-bottom: 1px solid var(--border);
}
.takeaway:last-child { border-bottom: none; }
.takeaway-bullet { color: var(--accent); font-weight: 700; font-size: 0.95rem; flex-shrink: 0; line-height: 1.6; }
.takeaway-text { color: var(--text-2); font-size: 0.87rem; line-height: 1.6; }

/* ── Glossary ── */
.gloss-card {
    background: var(--accent-dim); border: 1px solid var(--border-accent);
    border-radius: 10px; padding: 0.75rem 1rem; margin-bottom: 0.5rem;
}
.gloss-term { font-weight: 700; color: var(--accent); font-size: 0.85rem; margin-bottom: 2px; }
.gloss-trans { color: var(--text-1); font-size: 0.85rem; }
.gloss-exp { color: var(--text-2); font-size: 0.78rem; margin-top: 4px; }

/* ── Persona Cards (Onboarding) ── */
.persona-card {
    background: var(--bg-2); border: 2px solid var(--border);
    border-radius: 14px; padding: 1.5rem 1rem;
    cursor: pointer; transition: all 0.2s ease; text-align: center;
}
.persona-card:hover { border-color: var(--accent); box-shadow: var(--card-shadow-hover); }
.persona-card.selected {
    border-color: var(--accent); background: var(--accent-dim);
    box-shadow: 0 0 0 3px var(--accent-glow);
}
.persona-icon { font-size: 1.9rem; margin-bottom: 0.55rem; display: block; }
.persona-name { font-weight: 700; font-size: 0.92rem; color: var(--text-1); margin-bottom: 0.3rem; }
.persona-desc { color: var(--text-2); font-size: 0.76rem; line-height: 1.5; }

/* ── Home News Cards ── */
.home-news-card {
    background: var(--bg-2); border: 1px solid var(--border);
    border-left: 3px solid var(--accent); border-radius: 10px;
    padding: 0.95rem 1.1rem; margin-bottom: 0.7rem;
    box-shadow: var(--card-shadow);
    transition: border-color 0.18s, background 0.18s, box-shadow 0.18s;
}
.home-news-card:hover {
    border-left-color: var(--accent-hover);
    background: var(--bg-3); box-shadow: var(--card-shadow-hover);
}
.home-cat-pill {
    display: inline-block; background: var(--accent-dim);
    border: 1px solid var(--border-accent); color: var(--accent);
    font-size: 0.62rem; font-weight: 700; padding: 2px 8px;
    border-radius: 999px; text-transform: uppercase; letter-spacing: 0.08em; margin-right: 0.4rem;
}
.home-news-title { font-size: 0.93rem; font-weight: 600; color: var(--text-1); line-height: 1.4; margin: 0.3rem 0 0.38rem; }
.home-news-summary { color: var(--text-2); font-size: 0.81rem; line-height: 1.55; }
.home-news-time { color: var(--text-3); font-size: 0.68rem; }

/* ── My ET Feed Cards ── */
.news-card {
    background: var(--bg-2); border: 1px solid var(--border);
    border-left: 4px solid var(--accent); border-radius: 12px;
    padding: 1.2rem 1.4rem; margin-bottom: 0.9rem;
    box-shadow: var(--card-shadow);
    transition: border-color 0.18s, box-shadow 0.18s, transform 0.15s;
}
.news-card:hover { border-left-color: var(--accent-hover); box-shadow: var(--card-shadow-hover); transform: translateX(2px); }
.news-meta { display: flex; align-items: center; gap: 0.6rem; margin-bottom: 0.45rem; flex-wrap: wrap; }
.news-source { font-size: 0.68rem; font-weight: 700; color: var(--accent); text-transform: uppercase; letter-spacing: 0.1em; }
.news-time { color: var(--text-3); font-size: 0.68rem; }
.news-title { font-size: 1rem; font-weight: 600; color: var(--text-1); line-height: 1.4; margin-bottom: 0.45rem; }
.news-summary { color: var(--text-2); font-size: 0.83rem; line-height: 1.6; margin-bottom: 0.7rem; }

/* ── AI Snippet ── */
.ai-snippet {
    background: var(--accent-dim); border: 1px solid var(--border-accent);
    border-left: 3px solid var(--accent); border-radius: 8px; padding: 0.8rem 0.95rem; margin-top: 0.8rem;
}
.ai-snippet-label {
    font-size: 0.6rem; font-weight: 700; color: var(--accent);
    text-transform: uppercase; letter-spacing: 0.14em; margin-bottom: 0.3rem; display: block;
}
.ai-snippet-text { color: var(--text-1); font-size: 0.86rem; line-height: 1.65; font-style: italic; }

/* ── Tags ── */
.tag {
    display: inline-block; background: var(--bg-3); border: 1px solid var(--border);
    color: var(--text-2); font-size: 0.65rem; font-weight: 500;
    padding: 0.16rem 0.52rem; border-radius: 999px;
    margin-right: 0.28rem; text-transform: uppercase; letter-spacing: 0.05em;
}

/* ── Sentiment Dots ── */
.dot-positive { color: var(--positive); font-size: 0.7rem; }
.dot-negative { color: var(--negative); font-size: 0.7rem; }
.dot-neutral  { color: var(--text-3); font-size: 0.7rem; }

/* ── Deep Dive ── */
.deep-dive-section {
    background: var(--bg-2); border: 1px solid var(--border); border-radius: 10px;
    padding: 1rem 1.2rem; margin-bottom: 0.7rem; transition: border-color 0.18s;
}
.deep-dive-section:hover { border-color: var(--border-accent); }
.deep-dive-heading { font-size: 0.7rem; font-weight: 700; color: var(--accent); text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.4rem; }
.deep-dive-content { color: var(--text-1); font-size: 0.86rem; line-height: 1.7; }
.bottom-line {
    background: var(--accent-dim); border: 1px solid var(--border-accent);
    border-radius: 10px; padding: 1rem 1.2rem; margin-top: 1rem;
}
.bottom-line-label { font-size: 0.65rem; font-weight: 700; color: var(--gold); text-transform: uppercase; letter-spacing: 0.12em; margin-bottom: 0.3rem; display: block; }
.bottom-line-text { color: var(--text-1); font-size: 0.92rem; font-weight: 600; line-height: 1.5; }

/* ── Info / Error Boxes ── */
.err-box {
    background: var(--negative-dim); border: 1px solid rgba(248,113,113,0.25);
    border-radius: 10px; padding: 0.9rem 1rem; color: var(--negative); font-size: 0.85rem;
}
.info-box {
    background: var(--accent-dim); border: 1px solid var(--border-accent);
    border-radius: 10px; padding: 0.9rem 1rem; color: var(--text-2); font-size: 0.85rem;
}
.success-box {
    background: var(--positive-dim); border: 1px solid rgba(74,222,128,0.25);
    border-radius: 10px; padding: 0.9rem 1rem; color: var(--positive); font-size: 0.85rem;
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #8a0000, var(--accent)) !important;
    color: #fff !important; border: none !important; border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important; font-weight: 600 !important; font-size: 0.84rem !important;
    transition: opacity 0.18s, transform 0.1s, box-shadow 0.18s !important;
    box-shadow: 0 2px 8px var(--accent-glow) !important; letter-spacing: 0.01em !important;
}
.stButton > button:hover { opacity: 0.88 !important; transform: translateY(-1px) !important; box-shadow: 0 4px 14px var(--accent-glow) !important; }
.stButton > button:active { transform: translateY(0) !important; }

/* ── Inputs ── */
.stTextInput input, .stTextArea textarea {
    background: var(--input-bg) !important; border: 1px solid var(--border) !important;
    color: var(--text-1) !important; border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important; font-size: 0.9rem !important;
    transition: border-color 0.18s !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: var(--accent) !important; box-shadow: 0 0 0 2px var(--accent-dim) !important; outline: none !important;
}
.stTextInput input::placeholder, .stTextArea textarea::placeholder { color: var(--text-3) !important; }
.stSelectbox > div > div, .stMultiSelect > div > div {
    background: var(--input-bg) !important; border: 1px solid var(--border) !important;
    border-radius: 8px !important; color: var(--text-1) !important;
}
.stSelectbox [data-baseweb="select"] { background: var(--input-bg) !important; }

/* ── Radio ── */
div[data-testid="stRadio"] label { color: var(--text-1) !important; font-family: 'DM Sans', sans-serif !important; }

/* ── Metrics ── */
[data-testid="metric-container"] {
    background: var(--bg-2) !important; border: 1px solid var(--border) !important;
    border-top: 2px solid var(--accent) !important; border-radius: 10px !important;
    padding: 0.85rem 1rem !important; box-shadow: var(--card-shadow) !important;
}
[data-testid="stMetricValue"] { color: var(--text-1) !important; font-weight: 700 !important; font-family: 'DM Sans', sans-serif !important; }
[data-testid="stMetricLabel"] { color: var(--text-2) !important; font-size: 0.75rem !important; font-weight: 600 !important; text-transform: uppercase; letter-spacing: 0.06em; }

/* ── Expander ── */
details { border: 1px solid var(--border) !important; border-radius: 10px !important; background: var(--bg-2) !important; }
details summary { color: var(--text-2) !important; font-size: 0.84rem !important; font-weight: 600 !important; font-family: 'DM Sans', sans-serif !important; padding: 0.6rem 0 !important; }

/* ── Spinner ── */
.stSpinner > div { border-top-color: var(--accent) !important; }

/* ── Divider ── */
hr { border-color: var(--border) !important; margin: 0.75rem 0 !important; }

/* ── Sidebar logo block ── */
.sidebar-brand {
    padding: 1.2rem 1rem 0.8rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 0.75rem;
}
.sidebar-brand-name {
    font-family: 'Playfair Display', serif;
    font-size: 1.5rem; font-weight: 800; color: var(--text-1); line-height: 1;
}
.sidebar-brand-name span { color: var(--accent); }
.sidebar-badge {
    display: inline-block; margin-top: 5px;
    background: var(--accent-dim); border: 1px solid var(--border-accent);
    color: var(--accent); font-size: 0.6rem; font-weight: 700;
    letter-spacing: 0.12em; text-transform: uppercase; padding: 2px 9px; border-radius: 999px;
}

/* ── Category filter pills ── */
.cat-pill {
    display: inline-block; padding: 5px 14px;
    border-radius: 8px; font-size: 0.73rem; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.06em; text-align: center; width: 100%;
    cursor: pointer; border: 1px solid var(--border);
    background: var(--bg-2); color: var(--text-2);
    transition: all 0.15s;
}
.cat-pill-active {
    background: var(--accent-dim); border-color: var(--accent); color: var(--accent);
}

/* ── Feature strip ── */
.feature-strip-card {
    background: var(--bg-2); border: 1px solid var(--border);
    border-top: 2px solid var(--accent); border-radius: 10px;
    padding: 1rem; text-align: center; box-shadow: var(--card-shadow);
    transition: box-shadow 0.18s, border-color 0.18s;
}
.feature-strip-card:hover { box-shadow: var(--card-shadow-hover); border-top-color: var(--accent-hover); }
.feature-strip-icon { font-size: 1.5rem; margin-bottom: 0.35rem; display: block; }
.feature-strip-name { font-weight: 700; color: var(--text-1); font-size: 0.85rem; }
.feature-strip-desc { color: var(--text-3); font-size: 0.72rem; margin-top: 3px; }

/* ── Mode toggle button ── */
.mode-toggle-btn .stButton > button {
    background: var(--bg-3) !important;
    color: var(--text-1) !important;
    box-shadow: none !important;
    border: 1px solid var(--border) !important;
    font-size: 0.8rem !important;
}
.mode-toggle-btn .stButton > button:hover {
    border-color: var(--accent) !important;
    background: var(--accent-dim) !important;
    transform: none !important;
    box-shadow: none !important;
}

/* ── Plotly chart container ── */
.js-plotly-plot .plotly { border-radius: 10px !important; }

/* ── Vernacular article search results ── */
.search-result-card {
    background: var(--bg-2); border: 1px solid var(--border); border-radius: 10px;
    padding: 0.85rem 1.1rem; margin-bottom: 0.45rem;
    transition: border-color 0.18s, background 0.18s;
}
.search-result-card:hover { border-color: var(--border-accent); background: var(--bg-3); }
.search-result-card.selected { border-color: var(--accent); background: var(--accent-dim); }
.search-result-title { font-weight: 600; color: var(--text-1); font-size: 0.88rem; line-height: 1.4; }
.search-result-meta { color: var(--text-3); font-size: 0.72rem; margin-top: 2px; }
.search-result-summary { color: var(--text-2); font-size: 0.8rem; margin-top: 4px; line-height: 1.5; }

/* ── Highlights (contrarian / predictions) ── */
.insight-card {
    border-radius: 10px; padding: 1rem 1.2rem; margin-bottom: 0.9rem;
}
.insight-card-warning {
    background: var(--warning-dim); border: 1px solid rgba(251,191,36,0.2);
}
.insight-card-accent {
    background: var(--accent-dim); border: 1px solid var(--border-accent);
}
.insight-label { font-size: 0.68rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.12em; margin-bottom: 0.4rem; display: block; }
.insight-label-warning { color: var(--warning); }
.insight-label-accent { color: var(--accent); }
.insight-text { color: var(--text-1); font-size: 0.88rem; line-height: 1.7; }
"""

st.markdown(
    f"<style>:root{{{DARK_VARS if IS_DARK else LIGHT_VARS}}}{COMMON_CSS}</style>",
    unsafe_allow_html=True,
)

# ── Helper Functions ───────────────────────────────────────────────────────────

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


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        f"""
        <div class="sidebar-brand">
            <div class="sidebar-brand-name">ET_<span>Intelligence</span></div>
            <div class="sidebar-badge">Hackathon · Round 2</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    page = st.radio(
        "Navigation",
        ["🏠 Home", "📰 My ET — Newsroom", "📖 Story Arc Tracker", "📄 News Summarizer", "🌐 Vernacular Engine"],
        label_visibility="collapsed",
    )

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    # ── Dark / Light Toggle ──────────────────────────────────────────────────
    toggle_label = "☀️  Light Mode" if IS_DARK else "🌙  Dark Mode"
    st.markdown('<div class="mode-toggle-btn">', unsafe_allow_html=True)
    if st.button(toggle_label, use_container_width=True):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:0.25rem'></div>", unsafe_allow_html=True)
    st.markdown(f'<hr style="border-color:var(--border); margin:0.6rem 0;">', unsafe_allow_html=True)

    with st.expander("⚙️ Setup & Requirements", expanded=False):
        st.markdown(
            """
            <div style="font-size:0.78rem; line-height:1.9; color:var(--text-2);">
                <div><span style="color:var(--positive);">✓</span> Ollama running locally</div>
                <div><span style="color:var(--positive);">✓</span> <code>llama3.1:8b</code> pulled</div>
                <div style="margin-bottom:0.7rem;"><span style="color:var(--positive);">✓</span> Backend on port 8000</div>
                <div style="border-top:1px solid var(--border); padding-top:0.6rem; color:var(--text-3); font-size:0.72rem;">
                    <div style="margin-bottom:3px;">Start Ollama:</div>
                    <code style="color:var(--accent); font-size:0.7rem; display:block; margin-bottom:6px; font-family:'DM Mono',monospace;">ollama run llama3.1:8b</code>
                    <div style="margin-bottom:3px;">Start backend:</div>
                    <code style="color:var(--accent); font-size:0.7rem; display:block; font-family:'DM Mono',monospace;">uvicorn app.main:app --reload</code>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ═══════════════════════════════════════════════════════════════════════════════
# 🏠  HOME PAGE — Live ET General News Feed
# ═══════════════════════════════════════════════════════════════════════════════
if page == "🏠 Home":

    st.markdown(
        """
        <div class="et-header">
            <div class="et-logo"><span>ET_Intelligence</span></div>
            <div class="et-tagline">Live Economic Times · General News Feed</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_title, col_refresh = st.columns([7, 1])
    with col_title:
        st.markdown(
            """
            <div style="margin-bottom:0.2rem;">
                <span style="font-family:'Playfair Display',serif; font-size:1.7rem; font-weight:800; color:var(--text-1);">
                    Today's Business News
                </span>
            </div>
            <div style="color:var(--text-3); font-size:0.8rem;">
                Live from Economic Times RSS · Markets · Tech · Startups · Economy · Policy
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_refresh:
        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
        if st.button("↻ Refresh", use_container_width=True):
            st.session_state["home_articles"] = None
            st.rerun()

    st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

    # Fetch articles (cached per session)
    if st.session_state["home_articles"] is None:
        with st.spinner("📡 Fetching live ET articles…"):
            data, err = api_get("/articles/feed", {"max_per_feed": 15})
        if err:
            st.markdown(f'<div class="err-box">{err}</div>', unsafe_allow_html=True)
            st.stop()
        articles_raw = data.get("articles", [])
        for art in articles_raw:
            art["_category"] = _detect_category_client(art.get("title", ""), art.get("summary", ""))
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
    active_cat = st.session_state["home_category_filter"]
    for i, cat in enumerate(all_cats):
        with cat_cols[i]:
            is_active = active_cat == cat
            pill_cls = "cat-pill cat-pill-active" if is_active else "cat-pill"
            st.markdown(f'<div class="{pill_cls}">{cat}</div>', unsafe_allow_html=True)
            if st.button(cat, key=f"cat_{cat}", use_container_width=True):
                st.session_state["home_category_filter"] = cat
                st.rerun()

    st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

    filtered = articles_raw if active_cat == "All" else [a for a in articles_raw if a.get("_category") == active_cat]
    st.markdown(
        f'<div style="color:var(--text-3); font-size:0.76rem; margin-bottom:0.9rem;">'
        f'Showing <b style="color:var(--accent);">{len(filtered)}</b> articles'
        f'{" · " + active_cat if active_cat != "All" else ""}'
        f'</div>',
        unsafe_allow_html=True,
    )

    if not filtered:
        st.markdown('<div class="info-box">No articles found for this category. Try refreshing.</div>', unsafe_allow_html=True)
    else:
        col_a, col_b = st.columns(2)
        for idx, art in enumerate(filtered):
            title        = art.get("title", "Untitled")
            summary      = art.get("summary", "")
            source       = art.get("source", "ET")
            pub          = art.get("published", "")[:16]
            link         = art.get("link", "")
            cat          = art.get("_category", "General")
            summary_clean = _re.sub(r"<[^>]+>", "", summary)[:200]

            target_col = col_a if idx % 2 == 0 else col_b
            with target_col:
                st.markdown(
                    f"""
                    <div class="home-news-card">
                        <div style="display:flex; align-items:center; gap:0.45rem; margin-bottom:0.15rem;">
                            <span class="home-cat-pill">{cat}</span>
                            <span class="home-news-time">{source} · {pub}</span>
                        </div>
                        <div class="home-news-title">{title}</div>
                        <div class="home-news-summary">{summary_clean}{"…" if len(summary_clean) >= 200 else ""}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                btn_c1, btn_c2 = st.columns(2)
                with btn_c1:
                    if link:
                        st.markdown(
                            f'<a href="{link}" target="_blank" style="color:var(--accent); font-size:0.76rem; text-decoration:none; font-weight:600;">Read on ET →</a>',
                            unsafe_allow_html=True,
                        )
                with btn_c2:
                    if st.button("🗺️ Story Arc", key=f"home_arc_{idx}", use_container_width=True):
                        topic_words = title.split()[:4]
                        st.session_state["prefill_story_arc"] = " ".join(topic_words)
                        st.rerun()
                st.markdown("<div style='height:0.2rem'></div>", unsafe_allow_html=True)

    # Feature strip
    st.markdown("<div style='height:1.25rem'></div>", unsafe_allow_html=True)
    st.markdown('<div class="section-label">⚡ AI Features — Use the sidebar to explore</div>', unsafe_allow_html=True)
    f1, f2, f3, f4 = st.columns(4)
    features = [
        ("📰", "My ET", "Persona-aware AI feed"),
        ("🗺️", "Story Arc", "Topic visual narratives"),
        ("📄", "Summarizer", "Article digest in seconds"),
        ("🌐", "Vernacular", "Hindi · Tamil · Telugu · Bengali"),
    ]
    for col, (icon, name, desc) in zip([f1, f2, f3, f4], features):
        with col:
            st.markdown(
                f"""
                <div class="feature-strip-card">
                    <span class="feature-strip-icon">{icon}</span>
                    <div class="feature-strip-name">{name}</div>
                    <div class="feature-strip-desc">{desc}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


# ═══════════════════════════════════════════════════════════════════════════════
# 📰  MY ET — PERSONALIZED NEWSROOM
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "📰 My ET — Newsroom":

    st.markdown(
        """
        <div class="et-header">
            <div class="et-logo">My<span>ET</span></div>
            <div class="et-tagline">Your Personalized Newsroom · AI-Powered</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state.my_et_page == "onboarding":

        st.markdown(
            """
            <div style="max-width:660px; margin:0 auto; padding:1.5rem 0 1rem;">
                <div style="font-family:'Playfair Display',serif; font-size:2rem; font-weight:800; color:var(--text-1); line-height:1.2; margin-bottom:0.4rem;">
                    Who are you reading<br>the news as?
                </div>
                <div style="color:var(--text-2); font-size:0.92rem; margin-bottom:1.75rem; line-height:1.5;">
                    Tell us your role. We'll shape every headline for <em>your</em> world.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

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
                st.markdown(
                    f"""
                    <div class="{card_cls}">
                        <span class="persona-icon">{meta['icon']}</span>
                        <div class="persona-name">{meta['name']}</div>
                        <div class="persona-desc">{meta['desc']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button(f"Select {meta['name']}", key=f"persona_{key}", use_container_width=True):
                    st.session_state.persona = key
                    st.rerun()

        if st.session_state.persona:
            p = st.session_state.persona
            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown(
                f'<div style="font-family:\'Playfair Display\',serif; font-size:1.2rem; font-weight:700; color:var(--text-1); margin-bottom:1rem;">'
                f'Tell us more — as a <span style="color:var(--accent);">{PERSONAS[p]["name"]}</span></div>',
                unsafe_allow_html=True,
            )

            profile_data = {"persona_type": p, "user_id": st.session_state.user_id, "name": ""}

            if p == "investor":
                name = st.text_input("Your name (optional)", placeholder="e.g. Ravi")
                sectors = st.multiselect(
                    "Sectors you invest in",
                    ["Banking", "IT", "Pharma", "Auto", "FMCG", "Real Estate", "Energy", "Metals", "Telecom"],
                    default=["Banking", "IT"],
                )
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
                focus = st.multiselect(
                    "Strategic priorities",
                    ["Expansion", "Cost optimisation", "Digital transformation", "Talent", "M&A", "Exports"],
                    default=["Expansion"],
                )
                profile_data.update({
                    "name": name,
                    "interests": [industry.lower(), function.lower(), "policy", "corporate", "strategy"],
                    "executive_context": {
                        "industry": industry, "function": function, "company_size": size,
                        "strategic_focus": [f.lower() for f in focus],
                    },
                })

            st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
            if st.button("🚀  Build My Newsroom", use_container_width=True):
                with st.spinner("Setting up your personalized newsroom…"):
                    data, err = api_post("/my-et/profile/extended", profile_data)
                    if err:
                        st.error(err)
                    else:
                        st.session_state.profile = profile_data
                        st.session_state.my_et_page = "feed"
                        st.rerun()

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

        # Header row
        col_greeting, col_refresh, col_switch = st.columns([5, 1, 1])
        with col_greeting:
            name = profile.get("name", "").strip()
            greeting = f"Good morning, {name}! 👋" if name else "Good morning! 👋"
            meta = PERSONA_META.get(persona, {})
            st.markdown(
                f"""
                <div>
                    <div style="font-family:'Playfair Display',serif; font-size:1.55rem; font-weight:800; color:var(--text-1); margin-bottom:0.2rem;">{greeting}</div>
                    <div style="color:var(--text-2); font-size:0.83rem;">
                        {meta.get('icon','')} <b style="color:var(--accent);">{meta.get('name','')} Newsroom</b> · Live from Economic Times
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
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

        # Persona switcher
        st.markdown("<div style='height:0.9rem'></div>", unsafe_allow_html=True)
        st.markdown('<div class="section-label">⚡ Switch Persona — Watch the same news transform</div>', unsafe_allow_html=True)
        switch_cols = st.columns(4)
        for i, (key, meta) in enumerate(PERSONA_META.items()):
            with switch_cols[i]:
                is_active = persona == key
                label = f"{meta['icon']} {meta['name']}"
                if is_active:
                    st.markdown(
                        f'<div style="text-align:center; padding:0.45rem; background:var(--accent-dim); border:1px solid var(--accent); border-radius:8px; color:var(--accent); font-weight:700; font-size:0.82rem;">{label} ✓</div>',
                        unsafe_allow_html=True,
                    )
                else:
                    if st.button(label, key=f"switch_{key}", use_container_width=True):
                        st.session_state.persona = key
                        new_profile = {"persona_type": key, "user_id": user_id, "interests": [key]}
                        api_post("/my-et/profile/extended", new_profile)
                        st.session_state.briefing = None
                        st.session_state.profile = new_profile
                        st.rerun()

        st.markdown("<div style='height:0.9rem'></div>", unsafe_allow_html=True)

        # Fetch briefing
        if st.session_state.briefing is None:
            with st.spinner("⚡ Fetching live ET news & generating AI insights…"):
                data, err = api_get(f"/my-et/briefing/{user_id}", {"top_n": 5})
                if err:
                    st.error(err)
                    st.stop()
                st.session_state.briefing = data

        briefing = st.session_state.briefing
        articles = briefing.get("articles", [])
        positive_count = sum(1 for a in articles if a.get("sentiment") == "positive")

        m1, m2, m3, m4 = st.columns(4)
        with m1: st.metric("📰 Articles", briefing.get("total_articles", 0))
        with m2: st.metric("⚡ AI Insights", briefing.get("enriched_count", 0))
        with m3: st.metric("🎭 Persona", PERSONA_META.get(persona, {}).get("name", ""))
        with m4: st.metric("📊 Positive News", f"{positive_count}/{len(articles)}")

        # Deep dive panel
        if st.session_state.deep_dive_article:
            art = st.session_state.deep_dive_article
            with st.expander(f"🔍 Deep Dive: {art['title'][:55]}…", expanded=True):
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
                            st.markdown(
                                f"""
                                <div class="deep-dive-section">
                                    <div class="deep-dive-heading">{section.get('heading','')}</div>
                                    <div class="deep-dive-content">{section.get('content','')}</div>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )
                    if dd_data.get("bottom_line"):
                        st.markdown(
                            f"""
                            <div class="bottom-line">
                                <span class="bottom-line-label">⚡ Bottom Line for You</span>
                                <div class="bottom-line-text">{dd_data['bottom_line']}</div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                    if art.get("link"):
                        st.markdown(
                            f'<div style="margin-top:0.75rem;"><a href="{art["link"]}" target="_blank" style="color:var(--accent); font-size:0.84rem; font-weight:600; text-decoration:none;">Read full article on ET →</a></div>',
                            unsafe_allow_html=True,
                        )
                if st.button("✕ Close Deep Dive"):
                    st.session_state.deep_dive_article = None
                    st.rerun()

        st.markdown('<div class="section-label">📰 Your Feed</div>', unsafe_allow_html=True)

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

            snippet_html = (
                f"""
                <div class="ai-snippet">
                    <span class="ai-snippet-label">⚡ What this means for you</span>
                    <div class="ai-snippet-text">{snippet.replace("<", "&lt;").replace(">", "&gt;")}</div>
                </div>
                """
                if snippet else ""
            )

            st.markdown(
                f"""
                <div class="news-card">
                    <div class="news-meta">
                        <span class="news-source">{source}</span>
                        <span class="news-time">{pub}</span>
                        {sentiment_dot(sentiment)}
                        <span style="font-size:0.68rem; color:var(--text-3);">{sentiment.capitalize()}</span>
                    </div>
                    <div class="news-title">{title}</div>
                    <div class="news-summary">{summary}…</div>
                    <div>{render_tags(tags)}</div>
                    {snippet_html}
                </div>
                """,
                unsafe_allow_html=True,
            )

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
                        st.markdown(
                            f'<a href="{link}" target="_blank" style="color:var(--accent); font-size:0.78rem; text-decoration:none; font-weight:600;">Read on ET →</a>',
                            unsafe_allow_html=True,
                        )

            st.markdown("<div style='height:0.25rem'></div>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# 📖  STORY ARC TRACKER
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "📖 Story Arc Tracker":

    st.markdown(
        """
        <div class="et-header">
            <div class="et-logo">Story <span>Arc</span></div>
            <div class="et-tagline">Visual Business Narratives · AI-Powered</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="hero-banner">
            <div class="hero-title">🗺️ Story Arc Tracker</div>
            <div class="hero-sub">Enter any business topic. AI builds a complete visual narrative from live ET articles.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    prefill = st.session_state.get("prefill_story_arc", "")
    if prefill:
        st.session_state["prefill_story_arc"] = ""

    col_inp, col_btn = st.columns([4, 1])
    with col_inp:
        topic = st.text_input(
            "Topic", value=prefill,
            placeholder="e.g. Adani Group, Jio IPO, RBI rate cut, Zomato…",
            label_visibility="collapsed",
        )
    with col_btn:
        generate = st.button("⚡ Generate Arc", use_container_width=True)

    st.markdown(
        """
        <div style="color:var(--text-3); font-size:0.78rem; margin-top:-0.4rem; margin-bottom:1.1rem;">
            Try: &nbsp;
            <span style="color:var(--accent); font-weight:600;">Adani Group</span> &nbsp;·&nbsp;
            <span style="color:var(--accent); font-weight:600;">Reliance Jio IPO</span> &nbsp;·&nbsp;
            <span style="color:var(--accent); font-weight:600;">RBI rate cut</span> &nbsp;·&nbsp;
            <span style="color:var(--accent); font-weight:600;">Startups funding winter</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if prefill and topic:
        generate = True

    if generate and topic.strip():
        with st.spinner(f"🔍 Analysing '{topic}' across ET articles…"):
            data, err = api_post("/story-arc", {"topic": topic})

        if err:
            st.markdown(f'<div class="err-box">{err}</div>', unsafe_allow_html=True)
        elif data:
            m1, m2, m3, m4 = st.columns(4)
            with m1: st.metric("📰 Articles Analysed", data.get("article_count", 0))
            with m2: st.metric("📡 Data Source", data.get("data_source_badge", ""))
            last_up = data.get("last_updated", "")
            with m3: st.metric("🕒 Last Updated", last_up[:16] if last_up else "Just now")
            with m4: st.metric("📊 Sentiment", data.get("sentiment_trend", "mixed").capitalize())

            # Sentiment chart
            sentiment_data = data.get("sentiment_data", [])
            if sentiment_data:
                st.markdown('<div class="section-heading">📊 Article Sentiment</div>', unsafe_allow_html=True)
                df = pd.DataFrame(sentiment_data)
                pos_col = "#4ade80"
                neg_col = "#f87171"
                neu_col = "#6b6360"
                df["color"] = df["score"].apply(lambda s: pos_col if s >= 0.05 else (neg_col if s <= -0.05 else neu_col))
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=list(range(len(df))), y=df["score"],
                    marker_color=df["color"], marker_line_width=0,
                    hovertemplate="<b>%{customdata}</b><br>Score: %{y:.3f}<extra></extra>",
                    customdata=df["title"],
                ))
                fig.add_hline(y=0, line_color="rgba(255,255,255,0.1)" if IS_DARK else "rgba(0,0,0,0.1)", line_dash="dash")
                fig.add_hrect(y0=0.05, y1=1, fillcolor="rgba(74,222,128,0.04)", line_width=0)
                fig.add_hrect(y0=-1, y1=-0.05, fillcolor="rgba(248,113,113,0.04)", line_width=0)
                bg = "rgba(0,0,0,0)"
                grid = "rgba(255,255,255,0.05)" if IS_DARK else "rgba(0,0,0,0.05)"
                tick_color = "#4a4a4a" if IS_DARK else "#aaa6a2"
                fig.update_layout(
                    paper_bgcolor=bg, plot_bgcolor=bg,
                    xaxis=dict(showticklabels=False, gridcolor=grid, zeroline=False),
                    yaxis=dict(gridcolor=grid, tickfont=dict(color=tick_color, size=11), range=[-1, 1], zeroline=False),
                    margin=dict(l=0, r=0, t=8, b=8), height=210,
                )
                st.plotly_chart(fig, use_container_width=True)

            col_l, col_r = st.columns([3, 2])

            with col_l:
                # Timeline
                timeline = data.get("timeline", [])
                if timeline:
                    st.markdown('<div class="section-heading">📅 Event Timeline</div>', unsafe_allow_html=True)
                    for ev in timeline:
                        sig = ev.get("significance", "medium").lower()
                        st.markdown(
                            f"""
                            <div class="timeline-item">
                                <div class="timeline-dot timeline-dot-{sig}"></div>
                                <div>
                                    <div style="color:var(--text-3); font-size:0.72rem; font-weight:600; font-family:'DM Mono',monospace;">{ev.get('date','')}</div>
                                    <div style="color:var(--text-1); font-size:0.86rem; margin-top:3px; line-height:1.5;">{ev.get('event','')}</div>
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                # Sentiment summary
                sum_text = data.get("sentiment_summary", "")
                if sum_text:
                    st.markdown('<div class="section-heading">💬 Sentiment Analysis</div>', unsafe_allow_html=True)
                    st.markdown(
                        f"""
                        <div class="glass-card">
                            <div style="margin-bottom:0.5rem;">{trend_badge(data.get("sentiment_trend","mixed"))}</div>
                            <div style="color:var(--text-2); font-size:0.88rem; line-height:1.7;">{sum_text}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            with col_r:
                # Key players
                players = data.get("key_players", [])
                if players:
                    st.markdown('<div class="section-heading">👥 Key Players</div>', unsafe_allow_html=True)
                    for p in players[:6]:
                        stance = p.get("stance", "neutral").lower()
                        score = 0.1 if stance == "positive" else (-0.1 if stance == "negative" else 0)
                        st.markdown(
                            f"""
                            <div class="player-card">
                                <div class="player-name">{p.get('name','')}</div>
                                <div class="player-role">{p.get('role','')}</div>
                                <div style="margin-top:6px;">{sentiment_badge(score)}</div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

            # Contrarian view
            contrarian = data.get("contrarian_view", "")
            if contrarian:
                st.markdown('<div class="section-heading">🔄 Contrarian View</div>', unsafe_allow_html=True)
                st.markdown(
                    f"""
                    <div class="insight-card insight-card-warning">
                        <span class="insight-label insight-label-warning">⚠️ Alternative Perspective</span>
                        <div class="insight-text">{contrarian}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            # Predictions
            predictions = data.get("predictions", "")
            if predictions:
                st.markdown('<div class="section-heading">🔮 What to Watch</div>', unsafe_allow_html=True)
                st.markdown(
                    f"""
                    <div class="insight-card insight-card-accent">
                        <span class="insight-label insight-label-accent">✨ Future Outlook</span>
                        <div class="insight-text">{predictions}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    elif generate and not topic.strip():
        st.warning("Please enter a topic to analyse.")


# ═══════════════════════════════════════════════════════════════════════════════
# 📄  NEWS SUMMARIZER
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "📄 News Summarizer":

    st.markdown(
        """
        <div class="et-header">
            <div class="et-logo">News <span>Digest</span></div>
            <div class="et-tagline">AI Article Summarizer · Instant Insights</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="hero-banner">
            <div class="hero-title">📄 News Summarizer</div>
            <div class="hero-sub">Paste any article or URL. Get a crisp AI digest with key takeaways and contextual impact.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    input_mode = st.radio("Input type", ["📝 Paste Text", "🔗 Article URL"], horizontal=True)
    st.markdown("<div style='height:0.4rem'></div>", unsafe_allow_html=True)

    article_text = None
    article_url  = None

    if input_mode == "📝 Paste Text":
        article_text = st.text_area("Article text", placeholder="Paste the full article text here…", height=240, label_visibility="collapsed")
    else:
        article_url = st.text_input("Article URL", placeholder="https://economictimes.indiatimes.com/…", label_visibility="collapsed")

    summarize_btn = st.button("📄  Summarize Article", use_container_width=False)

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
            st.markdown(
                f"""
                <div class="glass-card" style="border-left:4px solid var(--accent);">
                    <div style="color:var(--text-1); font-size:0.96rem; line-height:1.8;">{data.get("summary", "Summary not available.")}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            takeaways = data.get("key_takeaways", [])
            if takeaways:
                st.markdown('<div class="section-heading">🎯 Key Takeaways</div>', unsafe_allow_html=True)
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                for i, t in enumerate(takeaways, 1):
                    st.markdown(
                        f"""
                        <div class="takeaway">
                            <span class="takeaway-bullet">{i}.</span>
                            <span class="takeaway-text">{t}</span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                st.markdown("</div>", unsafe_allow_html=True)

            impact = data.get("contextual_impact", "")
            if impact:
                st.markdown('<div class="section-heading">🌍 Contextual Impact</div>', unsafe_allow_html=True)
                st.markdown(
                    f"""
                    <div class="insight-card insight-card-accent">
                        <div style="color:var(--text-1); font-size:0.9rem; line-height:1.7;">{impact}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


# ═══════════════════════════════════════════════════════════════════════════════
# 🌐  VERNACULAR ENGINE
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "🌐 Vernacular Engine":

    st.markdown(
        """
        <div class="et-header">
            <div class="et-logo">Vernacular <span>Engine</span></div>
            <div class="et-tagline">Business News in Your Language</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="hero-banner">
            <div class="hero-title">🌐 Vernacular Engine</div>
            <div class="hero-sub">Search ET articles, paste a URL, or enter text — then translate with local cultural context and a terminology glossary.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    LANG_OPTIONS = {
        "🇮🇳 Hindi (हिंदी)": "hi",
        "🇮🇳 Tamil (தமிழ்)": "ta",
        "🇮🇳 Telugu (తెలుగు)": "te",
        "🇮🇳 Bengali (বাংলা)": "bn",
    }

    input_mode = st.radio(
        "Source",
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
            st.markdown(
                f'<div style="color:var(--text-3); font-size:0.77rem; margin-bottom:0.65rem;">{len(results)} articles found — click → to load one</div>',
                unsafe_allow_html=True,
            )
            for art in results:
                title   = art.get("title", "Untitled")
                summary = art.get("summary", "")[:160]
                pub     = art.get("published", "")[:16]
                link    = art.get("link", "")
                is_sel  = st.session_state.get("vern_article_title") == title
                card_cls = "search-result-card selected" if is_sel else "search-result-card"

                col_card, col_pick = st.columns([10, 1])
                with col_card:
                    st.markdown(
                        f"""
                        <div class="{card_cls}">
                            <div class="search-result-title">{title}</div>
                            <div class="search-result-meta">{pub}</div>
                            <div class="search-result-summary">{summary}…</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
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
            st.markdown(
                f"""
                <div class="success-box" style="margin-top:0.5rem;">
                    <b>✅ Selected:</b> {st.session_state['vern_article_title']}
                    <span style="float:right; opacity:0.6;">{len(st.session_state['vern_article_text']):,} chars</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

    elif input_mode == "🔗 Article URL":
        col_u, col_ub = st.columns([5, 1])
        with col_u:
            article_url = st.text_input("ET Article URL", placeholder="https://economictimes.indiatimes.com/…", label_visibility="collapsed")
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
                        st.markdown(f'<div class="success-box">✅ Fetched {fd.get("char_count", len(fetched)):,} characters</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="err-box">Could not extract text. Try the Paste Text mode.</div>', unsafe_allow_html=True)
                except Exception as e:
                    st.markdown(f'<div class="err-box">Fetch failed: {e}</div>', unsafe_allow_html=True)

        if st.session_state.get("vern_article_text"):
            with st.expander("📄 Preview fetched text", expanded=False):
                st.caption(st.session_state["vern_article_text"][:600] + "…")

    elif input_mode == "📝 Paste Text":
        pasted = st.text_area("Paste English business text", placeholder="Paste any English business news text here…", height=200, label_visibility="collapsed")
        if pasted.strip():
            st.session_state["vern_article_text"] = pasted.strip()
            st.session_state["vern_article_title"] = "Pasted text"

    st.markdown("<div style='height:0.85rem'></div>", unsafe_allow_html=True)

    col_lang, col_mod, col_tbtn = st.columns([2, 2, 1])
    with col_lang:
        selected_lang_label = st.selectbox("Target language", list(LANG_OPTIONS.keys()))
        selected_lang_code  = LANG_OPTIONS[selected_lang_label]
    with col_mod:
        selected_model = st.selectbox("Translation Model", ["llama3.1:8b", "aya:8b", "gemma2:9b", "qwen2.5:7b", "mistral:7b"])
    with col_tbtn:
        st.markdown("<div style='height:1.65rem'></div>", unsafe_allow_html=True)
        translate_btn = st.button(
            "🌐  Translate",
            use_container_width=True,
            disabled=not bool(st.session_state.get("vern_article_text")),
        )

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
            st.markdown('<div class="section-heading">📄 Translation Result</div>', unsafe_allow_html=True)

            col_orig, col_trans = st.columns(2)
            with col_orig:
                st.markdown(
                    '<div style="color:var(--text-3); font-size:0.72rem; font-weight:700; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:0.5rem;">🇬🇧 Original (English)</div>',
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f"""
                    <div class="glass-card" style="min-height:130px; max-height:320px; overflow-y:auto;">
                        <div style="color:var(--text-2); font-size:0.86rem; line-height:1.8;">{data.get('original','')[:1500]}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with col_trans:
                native     = data.get("target_language_native", "")
                eng        = data.get("target_language", "")
                flag       = data.get("flag", "🇮🇳")
                model_used = data.get("model_used", "")
                st.markdown(
                    f'<div style="color:var(--text-3); font-size:0.72rem; font-weight:700; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:0.5rem;">'
                    f'{flag} {eng} ({native}) &nbsp;·&nbsp; <span style="color:var(--accent);">{model_used}</span></div>',
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f"""
                    <div class="glass-card" style="min-height:130px; max-height:320px; overflow-y:auto; border-left:3px solid var(--accent);">
                        <div style="color:var(--text-1); font-size:0.95rem; line-height:1.95;">{data.get('improved_translation', data.get('base_translation',''))}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            context_note = data.get("local_context_note", "")
            if context_note:
                st.markdown('<div class="section-heading">📍 Local Context Note</div>', unsafe_allow_html=True)
                st.markdown(
                    f"""
                    <div class="insight-card insight-card-warning">
                        <span class="insight-label insight-label-warning">🗺️ For Local Readers</span>
                        <div class="insight-text">{context_note}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            glossary = data.get("terminology_glossary", [])
            if glossary:
                st.markdown('<div class="section-heading">📚 Business Terminology Glossary</div>', unsafe_allow_html=True)
                cols = st.columns(min(len(glossary), 3))
                for i, item in enumerate(glossary):
                    with cols[i % 3]:
                        st.markdown(
                            f"""
                            <div class="gloss-card">
                                <div class="gloss-term">{item.get('term','')}</div>
                                <div class="gloss-trans">{item.get('translation','')}</div>
                                <div class="gloss-exp">{item.get('explanation','')}</div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
