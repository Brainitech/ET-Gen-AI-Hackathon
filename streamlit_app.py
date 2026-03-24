"""
aether_ai — Streamlit Frontend
Premium dark glassmorphism UI | ET Hackathon Round 2
Features: Story Arc Tracker · News Summarizer · Vernacular Business News Engine
"""
import streamlit as st
import requests
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime

# ── Page Configuration ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="aether_ai — AI-Native Business News",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

API_BASE = "http://localhost:8000/api/v1"

# ── Global CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&display=swap');

/* Base */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}
.stApp {
    background: linear-gradient(135deg, #0a0a0f 0%, #0d1117 40%, #0a0f1e 100%);
    color: #e2e8f0;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1117 0%, #0a0a1a 100%);
    border-right: 1px solid rgba(99,102,241,0.2);
}
section[data-testid="stSidebar"] .stRadio label {
    color: #94a3b8;
    font-size: 0.9rem;
    transition: color 0.2s;
}
section[data-testid="stSidebar"] .stRadio label:hover { color: #e2e8f0; }

/* Hero banner */
.hero-banner {
    background: linear-gradient(135deg, rgba(99,102,241,0.15) 0%, rgba(168,85,247,0.1) 50%, rgba(59,130,246,0.1) 100%);
    border: 1px solid rgba(99,102,241,0.3);
    border-radius: 20px;
    padding: 2rem 2.5rem;
    margin-bottom: 2rem;
    backdrop-filter: blur(10px);
}
.hero-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2.4rem;
    font-weight: 700;
    background: linear-gradient(135deg, #818cf8, #c084fc, #60a5fa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0;
}
.hero-sub {
    color: #94a3b8;
    font-size: 1rem;
    margin-top: 0.5rem;
}

/* Glass cards */
.glass-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    backdrop-filter: blur(10px);
    transition: border-color 0.3s, box-shadow 0.3s;
}
.glass-card:hover {
    border-color: rgba(99,102,241,0.4);
    box-shadow: 0 0 20px rgba(99,102,241,0.1);
}

/* Sentiment badges */
.badge {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}
.badge-positive { background: rgba(34,197,94,0.15); color: #4ade80; border: 1px solid rgba(34,197,94,0.3); }
.badge-negative { background: rgba(239,68,68,0.15); color: #f87171; border: 1px solid rgba(239,68,68,0.3); }
.badge-neutral  { background: rgba(148,163,184,0.15); color: #94a3b8; border: 1px solid rgba(148,163,184,0.3); }
.badge-rising   { background: rgba(34,197,94,0.15); color: #4ade80; border: 1px solid rgba(34,197,94,0.3); }
.badge-falling  { background: rgba(239,68,68,0.15); color: #f87171; border: 1px solid rgba(239,68,68,0.3); }
.badge-mixed    { background: rgba(251,191,36,0.15); color: #fbbf24; border: 1px solid rgba(251,191,36,0.3); }
.badge-stable   { background: rgba(99,102,241,0.15); color: #818cf8; border: 1px solid rgba(99,102,241,0.3); }

/* Category pills */
.cat-markets  { background: rgba(99,102,241,0.15); color: #818cf8; border: 1px solid rgba(99,102,241,0.3); }
.cat-startup  { background: rgba(168,85,247,0.15); color: #c084fc; border: 1px solid rgba(168,85,247,0.3); }
.cat-policy   { background: rgba(59,130,246,0.15); color: #60a5fa; border: 1px solid rgba(59,130,246,0.3); }
.cat-macro    { background: rgba(20,184,166,0.15); color: #2dd4bf; border: 1px solid rgba(20,184,166,0.3); }
.cat-tech     { background: rgba(236,72,153,0.15); color: #f472b6; border: 1px solid rgba(236,72,153,0.3); }
.cat-general  { background: rgba(148,163,184,0.15); color: #94a3b8; border: 1px solid rgba(148,163,184,0.3); }

/* Section headings */
.section-heading {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.1rem;
    font-weight: 600;
    color: #818cf8;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin: 1.5rem 0 0.75rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid rgba(99,102,241,0.2);
}

/* Timeline items */
.timeline-item {
    display: flex;
    gap: 1rem;
    margin-bottom: 0.75rem;
    align-items: flex-start;
}
.timeline-dot {
    width: 10px; height: 10px;
    border-radius: 50%;
    background: #818cf8;
    margin-top: 5px;
    flex-shrink: 0;
    box-shadow: 0 0 8px rgba(129,140,248,0.5);
}
.timeline-dot-high   { background: #f87171; box-shadow: 0 0 8px rgba(248,113,113,0.5); }
.timeline-dot-medium { background: #fbbf24; box-shadow: 0 0 8px rgba(251,191,36,0.5); }
.timeline-dot-low    { background: #4ade80; box-shadow: 0 0 8px rgba(74,222,128,0.5); }

/* Player cards */
.player-card {
    background: rgba(99,102,241,0.05);
    border: 1px solid rgba(99,102,241,0.2);
    border-radius: 10px;
    padding: 0.75rem 1rem;
    margin-bottom: 0.5rem;
}
.player-name { font-weight: 600; color: #e2e8f0; font-size: 0.95rem; }
.player-role { color: #94a3b8; font-size: 0.82rem; margin-top: 2px; }

/* Takeaway bullets */
.takeaway {
    display: flex;
    align-items: flex-start;
    gap: 0.75rem;
    padding: 0.6rem 0;
    border-bottom: 1px solid rgba(255,255,255,0.05);
}
.takeaway:last-child { border-bottom: none; }
.takeaway-bullet {
    color: #818cf8;
    font-weight: 700;
    font-size: 1rem;
    flex-shrink: 0;
}
.takeaway-text { color: #cbd5e1; font-size: 0.9rem; line-height: 1.5; }

/* Language flag button */
.lang-btn {
    border: 1px solid rgba(99,102,241,0.3);
    border-radius: 10px;
    padding: 0.5rem 1rem;
    background: rgba(99,102,241,0.07);
    cursor: pointer;
    transition: all 0.2s;
    text-align: center;
    font-size: 1.1rem;
}

/* Glossary cards */
.gloss-card {
    background: rgba(16,185,129,0.05);
    border: 1px solid rgba(16,185,129,0.2);
    border-radius: 10px;
    padding: 0.75rem 1rem;
    margin-bottom: 0.5rem;
}
.gloss-term { font-weight: 600; color: #34d399; font-size: 0.9rem; }
.gloss-trans { color: #e2e8f0; font-size: 0.9rem; }
.gloss-exp { color: #94a3b8; font-size: 0.82rem; margin-top: 4px; }

/* Streamlit button override */
.stButton>button {
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    color: white;
    border: none;
    border-radius: 10px;
    padding: 0.5rem 1.5rem;
    font-weight: 600;
    font-family: 'Inter', sans-serif;
    transition: opacity 0.2s, transform 0.1s;
    width: 100%;
}
.stButton>button:hover { opacity: 0.85; transform: translateY(-1px); }

/* Input fields */
.stTextInput input, .stTextArea textarea, .stSelectbox select {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
}

/* Error / warning */
.err-box {
    background: rgba(239,68,68,0.1);
    border: 1px solid rgba(239,68,68,0.3);
    border-radius: 10px;
    padding: 1rem;
    color: #fca5a5;
}
.info-box {
    background: rgba(59,130,246,0.07);
    border: 1px solid rgba(59,130,246,0.2);
    border-radius: 10px;
    padding: 1rem;
    color: #93c5fd;
}
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────
def api_post(endpoint: str, payload: dict):
    try:
        r = requests.post(f"{API_BASE}{endpoint}", json=payload, timeout=120)
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


def sentiment_badge(score: float) -> str:
    if score >= 0.05:
        return '<span class="badge badge-positive">● Positive</span>'
    elif score <= -0.05:
        return '<span class="badge badge-negative">● Negative</span>'
    return '<span class="badge badge-neutral">● Neutral</span>'


def trend_badge(trend: str) -> str:
    cls = f"badge badge-{trend.lower()}" if trend.lower() in ["rising","falling","mixed","stable"] else "badge badge-neutral"
    icons = {"rising":"↑","falling":"↓","mixed":"⟳","stable":"→"}
    icon = icons.get(trend.lower(), "•")
    return f'<span class="{cls}">{icon} {trend.capitalize()}</span>'


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding: 1rem 0 1.5rem; text-align:center;">
        <div style="font-family:'Space Grotesk',sans-serif; font-size:1.6rem; font-weight:700;
             background:linear-gradient(135deg,#818cf8,#c084fc); -webkit-background-clip:text;
             -webkit-text-fill-color:transparent; background-clip:text;">⚡ aether_ai</div>
        <div style="color:#475569; font-size:0.75rem; margin-top:4px;">ET Hackathon · Round 2</div>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "Navigate",
        ["🏠 Home", "📖 Story Arc Tracker", "📰 News Summarizer", "🌐 Vernacular Engine"],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown("""
    <div style="color:#475569; font-size:0.75rem; padding: 0 0.5rem;">
        <div style="margin-bottom:0.5rem; color:#64748b; font-weight:500;">Requirements</div>
        <div>✅ Ollama running locally</div>
        <div style="margin-top:4px;">✅ <code style="color:#818cf8">llama3.1:8b</code> pulled</div>
        <div style="margin-top:4px;">✅ Backend on port 8000</div>
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# HOME PAGE
# ═══════════════════════════════════════════════════════════════════════════════
if page == "🏠 Home":
    st.markdown("""
    <div class="hero-banner">
        <p class="hero-title">⚡ aether_ai</p>
        <p class="hero-sub">AI-Native Business News · Powered by Ollama · 100% Free & Open Source</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="glass-card" style="text-align:center; padding:2rem 1.5rem;">
            <div style="font-size:2.5rem; margin-bottom:1rem;">🗺️</div>
            <div style="font-family:'Space Grotesk',sans-serif; font-size:1.1rem; font-weight:600; color:#e2e8f0; margin-bottom:0.5rem;">Story Arc Tracker</div>
            <div style="color:#94a3b8; font-size:0.85rem; line-height:1.6;">Pick any business story. Get a complete visual narrative — timeline, key players, sentiment shifts, contrarian views & predictions.</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="glass-card" style="text-align:center; padding:2rem 1.5rem;">
            <div style="font-size:2.5rem; margin-bottom:1rem;">📰</div>
            <div style="font-family:'Space Grotesk',sans-serif; font-size:1.1rem; font-weight:600; color:#e2e8f0; margin-bottom:0.5rem;">News Summarizer</div>
            <div style="color:#94a3b8; font-size:0.85rem; line-height:1.6;">Paste any article or URL. Get a crisp 3-sentence summary plus 5 actionable key takeaways in seconds.</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="glass-card" style="text-align:center; padding:2rem 1.5rem;">
            <div style="font-size:2.5rem; margin-bottom:1rem;">🌐</div>
            <div style="font-family:'Space Grotesk',sans-serif; font-size:1.1rem; font-weight:600; color:#e2e8f0; margin-bottom:0.5rem;">Vernacular Engine</div>
            <div style="color:#94a3b8; font-size:0.85rem; line-height:1.6;">Real-time, culturally-adapted translation into Hindi, Tamil, Telugu & Bengali with local context notes.</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class="glass-card" style="margin-top:1rem;">
        <div class="section-heading">⚡ Quick Start</div>
        <div style="color:#94a3b8; font-size:0.88rem; line-height:2;">
            <b style="color:#e2e8f0;">1.</b> Make sure Ollama is running: <code style="color:#818cf8; background:rgba(99,102,241,0.1); padding:2px 8px; border-radius:4px;">ollama run llama3.1:8b</code><br/>
            <b style="color:#e2e8f0;">2.</b> Start the backend: <code style="color:#818cf8; background:rgba(99,102,241,0.1); padding:2px 8px; border-radius:4px;">uvicorn app.main:app --reload</code><br/>
            <b style="color:#e2e8f0;">3.</b> Use the sidebar to navigate to any feature →
        </div>
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# STORY ARC TRACKER
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "📖 Story Arc Tracker":
    st.markdown("""
    <div class="hero-banner">
        <p class="hero-title">🗺️ Story Arc Tracker</p>
        <p class="hero-sub">Enter any business topic. AI builds a complete visual narrative from live ET articles.</p>
    </div>
    """, unsafe_allow_html=True)

    col_inp, col_btn = st.columns([4, 1])
    with col_inp:
        topic = st.text_input(
            "Business topic",
            placeholder="e.g. Adani Group, Jio IPO, RBI rate cut, Zomato…",
            label_visibility="collapsed",
        )
    with col_btn:
        generate = st.button("⚡ Generate Arc", use_container_width=True)

    # Example topics
    st.markdown("""
    <div style="color:#475569; font-size:0.8rem; margin-top:-0.5rem; margin-bottom:1rem;">
        Try: &nbsp;
        <span style="color:#818cf8;">Adani Group</span> &nbsp;·&nbsp;
        <span style="color:#818cf8;">Reliance Jio IPO</span> &nbsp;·&nbsp;
        <span style="color:#818cf8;">RBI rate cut</span> &nbsp;·&nbsp;
        <span style="color:#818cf8;">Startups funding winter</span>
    </div>
    """, unsafe_allow_html=True)

    if generate and topic.strip():
        with st.spinner(f"🔍 Analysing {len([topic])} topic across ET articles…"):
            data, err = api_post("/story-arc", {"topic": topic})

        if err:
            st.markdown(f'<div class="err-box">{err}</div>', unsafe_allow_html=True)
        elif data:
            # ── Stats bar ─────────────────────────────────────────────────────
            m1, m2, m3, m4 = st.columns(4)
            with m1:
                st.metric("📰 Articles Analysed", data.get("article_count", 0))
            with m2:
                st.metric("📅 Timeline Events", len(data.get("timeline", [])))
            with m3:
                st.metric("👥 Key Players", len(data.get("key_players", [])))
            with m4:
                trend = data.get("sentiment_trend", "mixed")
                st.metric("📊 Sentiment Trend", trend.capitalize())

            # ── Sentiment chart ───────────────────────────────────────────────
            sentiment_data = data.get("sentiment_data", [])
            if sentiment_data:
                st.markdown('<div class="section-heading">📊 Sentiment Over Articles</div>', unsafe_allow_html=True)
                df = pd.DataFrame(sentiment_data)
                df["color"] = df["score"].apply(
                    lambda s: "#4ade80" if s >= 0.05 else ("#f87171" if s <= -0.05 else "#94a3b8")
                )
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=list(range(len(df))),
                    y=df["score"],
                    marker_color=df["color"],
                    hovertemplate="<b>%{customdata}</b><br>Score: %{y:.3f}<extra></extra>",
                    customdata=df["title"],
                ))
                fig.add_hline(y=0, line_color="rgba(255,255,255,0.2)", line_dash="dash")
                fig.add_hrect(y0=0.05, y1=1, fillcolor="rgba(74,222,128,0.05)", line_width=0)
                fig.add_hrect(y0=-1, y1=-0.05, fillcolor="rgba(248,113,113,0.05)", line_width=0)
                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    xaxis=dict(showticklabels=False, gridcolor="rgba(255,255,255,0.05)"),
                    yaxis=dict(gridcolor="rgba(255,255,255,0.05)", tickfont=dict(color="#94a3b8"), range=[-1, 1]),
                    margin=dict(l=0, r=0, t=10, b=10),
                    height=220,
                )
                st.plotly_chart(fig, use_container_width=True)

            col_l, col_r = st.columns([3, 2])

            # ── Timeline ──────────────────────────────────────────────────────
            with col_l:
                timeline = data.get("timeline", [])
                if timeline:
                    st.markdown('<div class="section-heading">📅 Event Timeline</div>', unsafe_allow_html=True)
                    for ev in timeline:
                        sig = ev.get("significance", "medium").lower()
                        dot_cls = f"timeline-dot-{sig}"
                        st.markdown(f"""
                        <div class="timeline-item">
                            <div class="timeline-dot {dot_cls}"></div>
                            <div>
                                <div style="color:#94a3b8; font-size:0.75rem;">{ev.get('date','')}</div>
                                <div style="color:#e2e8f0; font-size:0.88rem; margin-top:2px;">{ev.get('event','')}</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                # ── Sentiment summary ─────────────────────────────────────────
                sum_text = data.get("sentiment_summary", "")
                if sum_text:
                    st.markdown('<div class="section-heading">💬 Sentiment Analysis</div>', unsafe_allow_html=True)
                    st.markdown(f"""
                    <div class="glass-card">
                        <div style="margin-bottom:0.5rem;">{trend_badge(data.get("sentiment_trend","mixed"))}</div>
                        <div style="color:#cbd5e1; font-size:0.9rem; line-height:1.6;">{sum_text}</div>
                    </div>
                    """, unsafe_allow_html=True)

            # ── Key players ───────────────────────────────────────────────────
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


            # ── Contrarian view ───────────────────────────────────────────────
            contrarian = data.get("contrarian_view", "")
            if contrarian:
                st.markdown('<div class="section-heading">🔄 Contrarian View</div>', unsafe_allow_html=True)
                st.markdown(f"""
                <div class="glass-card" style="border-color:rgba(251,191,36,0.3);">
                    <div style="color:#fbbf24; font-size:0.85rem; font-weight:600; margin-bottom:0.5rem;">⚠️ Alternative Perspective</div>
                    <div style="color:#cbd5e1; font-size:0.9rem; line-height:1.7;">{contrarian}</div>
                </div>
                """, unsafe_allow_html=True)

    elif generate and not topic.strip():
        st.warning("Please enter a topic to analyse.")


# ═══════════════════════════════════════════════════════════════════════════════
# NEWS SUMMARIZER
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "📰 News Summarizer":
    st.markdown("""
    <div class="hero-banner">
        <p class="hero-title">📰 News Summarizer</p>
        <p class="hero-sub">Paste any article or URL. Get a crisp AI summary with key takeaways.</p>
    </div>
    """, unsafe_allow_html=True)

    input_mode = st.radio("Input type", ["📝 Paste Text", "🔗 Article URL"], horizontal=True)
    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    article_text = None
    article_url = None

    if input_mode == "📝 Paste Text":
        article_text = st.text_area(
            "Article text",
            placeholder="Paste the full article text here…",
            height=260,
            label_visibility="collapsed",
        )
    else:
        article_url = st.text_input(
            "Article URL",
            placeholder="https://economictimes.indiatimes.com/...",
            label_visibility="collapsed",
        )

    summarize_btn = st.button("📰 Summarize Article", use_container_width=False)

    if summarize_btn:
        payload = {}
        if article_text:
            payload["text"] = article_text
        elif article_url:
            payload["url"] = article_url
        else:
            st.warning("Please paste text or enter a URL.")
            st.stop()

        with st.spinner("🤖 Generating summary…"):
            data, err = api_post("/summarize", payload)

        if err:
            st.markdown(f'<div class="err-box">{err}</div>', unsafe_allow_html=True)
        elif data:
            # ── Metadata bar ──────────────────────────────────────────────────
            cat = data.get("category", "general")
            read_time = data.get("read_time_min", 1)
            m1, m2, m3 = st.columns(3)
            with m1:
                st.metric("🏷️ Category", cat.capitalize())
            with m2:
                st.metric("⏱️ Read Time", f"{read_time} min")
            with m3:
                st.metric("📏 Article Length", f"{data.get('char_count',0):,} chars")

            # ── Summary ───────────────────────────────────────────────────────
            st.markdown('<div class="section-heading">💡 AI Summary</div>', unsafe_allow_html=True)
            st.markdown(f"""
            <div class="glass-card" style="border-color:rgba(99,102,241,0.35);">
                <div style="color:#e2e8f0; font-size:1rem; line-height:1.8;">
                    {data.get("summary", "Summary not available.")}
                </div>
            </div>
            """, unsafe_allow_html=True)

            # ── Key takeaways ─────────────────────────────────────────────────
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


# ═══════════════════════════════════════════════════════════════════════════════
# VERNACULAR ENGINE
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "🌐 Vernacular Engine":
    st.markdown("""
    <div class="hero-banner">
        <p class="hero-title">🌐 Vernacular Business News Engine</p>
        <p class="hero-sub">Search ET articles, enter a URL, or paste text — then translate with local cultural context.</p>
    </div>
    """, unsafe_allow_html=True)

    LANG_OPTIONS = {
        "🇮🇳 Hindi (हिंदी)": "hi",
        "🇮🇳 Tamil (தமிழ்)": "ta",
        "🇮🇳 Telugu (తెలుగు)": "te",
        "🇮🇳 Bengali (বাংলা)": "bn",
    }

    # ── Input mode selector ───────────────────────────────────────────────────
    input_mode = st.radio(
        "How to find the article",
        ["🔍 Search ET Articles", "🔗 Article URL", "📝 Paste Text"],
        horizontal=True,
        label_visibility="collapsed",
    )
    st.markdown("<div style='height:0.25rem'></div>", unsafe_allow_html=True)

    # Session state — persist selected article across reruns
    if "vern_article_text" not in st.session_state:
        st.session_state["vern_article_text"] = ""
    if "vern_article_title" not in st.session_state:
        st.session_state["vern_article_title"] = ""
    if "vern_search_results" not in st.session_state:
        st.session_state["vern_search_results"] = []

    # ── Mode 1: Search ET Articles ────────────────────────────────────────────
    if input_mode == "🔍 Search ET Articles":
        col_s, col_sb = st.columns([5, 1])
        with col_s:
            search_query = st.text_input(
                "Search ET",
                placeholder="e.g. RBI rate cut, Infosys earnings, startup funding…",
                label_visibility="collapsed",
            )
        with col_sb:
            do_search = st.button("🔍 Search", use_container_width=True)

        if do_search and search_query.strip():
            with st.spinner("Searching ET articles…"):
                try:
                    r = requests.get(
                        "http://localhost:8000/api/v1/articles/search",
                        params={"q": search_query},
                        timeout=15,
                    )
                    r.raise_for_status()
                    st.session_state["vern_search_results"] = r.json().get("articles", [])
                    # Clear previous selection when searching
                    st.session_state["vern_article_text"] = ""
                    st.session_state["vern_article_title"] = ""
                except Exception as e:
                    st.markdown(f'<div class="err-box">Search failed: {e}</div>', unsafe_allow_html=True)

        # Show search results as selectable cards
        results = st.session_state.get("vern_search_results", [])
        if results:
            st.markdown(
                f'<div style="color:#64748b; font-size:0.8rem; margin-bottom:0.75rem;">'
                f'{len(results)} articles found — click → to load one</div>',
                unsafe_allow_html=True,
            )
            for art in results:
                title = art.get("title", "Untitled")
                summary = art.get("summary", "")[:160]
                pub = art.get("published", "")[:16]
                link = art.get("link", "")
                is_selected = st.session_state.get("vern_article_title") == title
                border_col = "rgba(99,102,241,0.6)" if is_selected else "rgba(255,255,255,0.07)"
                bg_col = "rgba(99,102,241,0.08)" if is_selected else "rgba(255,255,255,0.02)"

                col_card, col_pick = st.columns([10, 1])
                with col_card:
                    st.markdown(f"""
                    <div class="glass-card" style="padding:0.85rem 1.1rem; border-color:{border_col}; background:{bg_col}; margin-bottom:0.4rem;">
                        <div style="font-weight:600; color:#e2e8f0; font-size:0.9rem;">{title}</div>
                        <div style="color:#64748b; font-size:0.75rem; margin-top:2px;">{pub}</div>
                        <div style="color:#94a3b8; font-size:0.82rem; margin-top:4px; line-height:1.5;">{summary}…</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col_pick:
                    btn_label = "✓" if is_selected else "→"
                    if st.button(btn_label, key=f"pick_{link}", use_container_width=True):
                        with st.spinner("Fetching full article…"):
                            try:
                                fr = requests.get(
                                    "http://localhost:8000/api/v1/articles/fetch",
                                    params={"url": link},
                                    timeout=20,
                                )
                                fr.raise_for_status()
                                fetched = fr.json().get("text", "")
                                st.session_state["vern_article_text"] = fetched if fetched else (
                                    art.get("title", "") + ". " + art.get("summary", "")
                                )
                            except Exception:
                                st.session_state["vern_article_text"] = (
                                    art.get("title", "") + ". " + art.get("summary", "")
                                )
                            st.session_state["vern_article_title"] = title
                        st.rerun()

        # Selected article badge
        if st.session_state.get("vern_article_title"):
            st.markdown(f"""
            <div class="glass-card" style="border-color:rgba(99,102,241,0.4); margin-top:0.5rem; padding:0.85rem 1.1rem;">
                <div style="color:#818cf8; font-size:0.78rem; font-weight:600; text-transform:uppercase; letter-spacing:0.08em;">✅ Selected Article</div>
                <div style="color:#e2e8f0; font-size:0.9rem; font-weight:500; margin-top:6px;">{st.session_state['vern_article_title']}</div>
                <div style="color:#64748b; font-size:0.78rem; margin-top:4px;">{len(st.session_state['vern_article_text']):,} characters loaded</div>
            </div>
            """, unsafe_allow_html=True)

    # ── Mode 2: URL Input ─────────────────────────────────────────────────────
    elif input_mode == "🔗 Article URL":
        col_u, col_ub = st.columns([5, 1])
        with col_u:
            article_url = st.text_input(
                "ET Article URL",
                placeholder="https://economictimes.indiatimes.com/...",
                label_visibility="collapsed",
            )
        with col_ub:
            fetch_btn = st.button("📥 Fetch", use_container_width=True)

        if fetch_btn and article_url.strip():
            with st.spinner("Fetching article…"):
                try:
                    fr = requests.get(
                        "http://localhost:8000/api/v1/articles/fetch",
                        params={"url": article_url.strip()},
                        timeout=20,
                    )
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

    # ── Mode 3: Paste Text ────────────────────────────────────────────────────
    elif input_mode == "📝 Paste Text":
        pasted = st.text_area(
            "Paste English business text",
            placeholder="Paste any English business news text here…",
            height=200,
            label_visibility="collapsed",
        )
        if pasted.strip():
            st.session_state["vern_article_text"] = pasted.strip()
            st.session_state["vern_article_title"] = "Pasted text"

    # ── Language selector + Translate button (shared) ─────────────────────────
    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    col_lang, col_tbtn = st.columns([3, 1])
    with col_lang:
        selected_lang_label = st.selectbox("Target language", list(LANG_OPTIONS.keys()))
        selected_lang_code = LANG_OPTIONS[selected_lang_label]
    with col_tbtn:
        st.markdown("<div style='height:1.75rem'></div>", unsafe_allow_html=True)
        translate_btn = st.button(
            "🌐 Translate",
            use_container_width=True,
            disabled=not bool(st.session_state.get("vern_article_text")),
        )

    # ── Translation output ────────────────────────────────────────────────────
    if translate_btn and st.session_state.get("vern_article_text"):
        lang_display = selected_lang_label.split("(")[0].strip()
        with st.spinner(f"Translating to {lang_display}…"):
            data, err = api_post("/translate", {
                "text": st.session_state["vern_article_text"][:4000],
                "target_lang": selected_lang_code,
            })

        if err:
            st.markdown(f'<div class="err-box">{err}</div>', unsafe_allow_html=True)
        elif data:
            st.markdown('<div class="section-heading">📄 Translation</div>', unsafe_allow_html=True)
            col_orig, col_trans = st.columns(2)
            with col_orig:
                st.markdown('<div style="color:#64748b; font-size:0.75rem; font-weight:600; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:0.5rem;">🇬🇧 Original (English)</div>', unsafe_allow_html=True)
                st.markdown(f"""
                <div class="glass-card" style="min-height:130px; max-height:320px; overflow-y:auto;">
                    <div style="color:#cbd5e1; font-size:0.88rem; line-height:1.8;">{data.get('original','')[:1500]}</div>
                </div>
                """, unsafe_allow_html=True)
            with col_trans:
                native = data.get("target_language_native", "")
                eng = data.get("target_language", "")
                flag = data.get("flag", "🇮🇳")
                st.markdown(f'<div style="color:#64748b; font-size:0.75rem; font-weight:600; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:0.5rem;">{flag} Translated ({eng} · {native})</div>', unsafe_allow_html=True)
                st.markdown(f"""
                <div class="glass-card" style="min-height:130px; max-height:320px; overflow-y:auto; border-color:rgba(99,102,241,0.35);">
                    <div style="color:#e2e8f0; font-size:0.95rem; line-height:1.9;">{data.get('improved_translation', data.get('base_translation',''))}</div>
                </div>
                """, unsafe_allow_html=True)

            context_note = data.get("local_context_note", "")
            if context_note:
                st.markdown('<div class="section-heading">📍 Local Context Note</div>', unsafe_allow_html=True)
                st.markdown(f"""
                <div class="glass-card" style="border-color:rgba(251,191,36,0.3);">
                    <div style="color:#fbbf24; font-size:0.8rem; font-weight:600; margin-bottom:0.5rem;">🗺️ FOR LOCAL READERS</div>
                    <div style="color:#cbd5e1; font-size:0.9rem; line-height:1.7;">{context_note}</div>
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
