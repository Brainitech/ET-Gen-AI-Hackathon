"""
ET-Pulse Streamlit Frontend.

A premium, dark-themed dashboard connecting to all 5 ET-Pulse
FastAPI backend features.

Run:
    streamlit run streamlit_app.py
"""

import json
import time
from datetime import datetime

import httpx
import plotly.graph_objects as go
import streamlit as st

# ------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------

API_BASE = "http://localhost:8000/api/v1"
TIMEOUT = 60.0

# ------------------------------------------------------------------
# Page config & custom CSS
# ------------------------------------------------------------------

st.set_page_config(
    page_title="ET-Pulse • AI News Platform",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

    /* ---------- Root variables ---------- */
    :root {
        --bg-primary: #0a0a0f;
        --bg-secondary: #12121a;
        --bg-card: #1a1a2e;
        --bg-card-hover: #222240;
        --accent-primary: #6c63ff;
        --accent-secondary: #ff6584;
        --accent-glow: rgba(108, 99, 255, 0.25);
        --text-primary: #eaeaff;
        --text-secondary: #9d9db5;
        --text-muted: #6b6b80;
        --border-subtle: rgba(108, 99, 255, 0.15);
        --gradient-hero: linear-gradient(135deg, #6c63ff 0%, #ff6584 50%, #f5a623 100%);
        --success: #00e676;
        --warning: #ffab40;
        --danger: #ff5252;
    }

    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', sans-serif !important;
        background: var(--bg-primary) !important;
        color: var(--text-primary) !important;
    }

    [data-testid="stSidebar"] {
        background: var(--bg-secondary) !important;
        border-right: 1px solid var(--border-subtle) !important;
    }

    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] .stMarkdown li,
    [data-testid="stSidebar"] label {
        color: var(--text-secondary) !important;
    }

    /* ---------- Headers ---------- */
    h1, h2, h3 {
        font-family: 'Inter', sans-serif !important;
        font-weight: 800 !important;
        letter-spacing: -0.02em !important;
    }
    h1 { color: var(--text-primary) !important; }
    h2 { color: var(--text-primary) !important; }
    h3 { color: var(--accent-primary) !important; }

    /* ---------- Hero badge ---------- */
    .hero-badge {
        background: var(--gradient-hero);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.8rem;
        font-weight: 900;
        letter-spacing: -0.03em;
        line-height: 1.1;
        margin-bottom: 0;
    }
    .hero-sub {
        color: var(--text-secondary);
        font-size: 1.05rem;
        font-weight: 400;
        margin-top: 4px;
    }

    /* ---------- Glass cards ---------- */
    .glass-card {
        background: rgba(26, 26, 46, 0.7);
        backdrop-filter: blur(12px);
        border: 1px solid var(--border-subtle);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 16px;
        transition: all 0.3s ease;
    }
    .glass-card:hover {
        border-color: var(--accent-primary);
        box-shadow: 0 0 30px var(--accent-glow);
        transform: translateY(-2px);
    }

    /* ---------- Stat pill ---------- */
    .stat-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(108, 99, 255, 0.12);
        border: 1px solid var(--border-subtle);
        border-radius: 999px;
        padding: 6px 14px;
        font-size: 0.82rem;
        font-weight: 600;
        color: var(--accent-primary);
    }

    /* ---------- Sentiment badges ---------- */
    .sentiment-positive { color: var(--success); font-weight: 700; }
    .sentiment-negative { color: var(--danger); font-weight: 700; }
    .sentiment-neutral  { color: var(--warning); font-weight: 700; }
    .sentiment-mixed    { color: var(--accent-primary); font-weight: 700; }

    /* ---------- Buttons ---------- */
    .stButton > button {
        background: var(--gradient-hero) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        font-family: 'Inter', sans-serif !important;
        padding: 0.55rem 1.6rem !important;
        transition: all 0.3s ease !important;
        letter-spacing: 0.01em !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px var(--accent-glow) !important;
    }

    /* ---------- Inputs ---------- */
    .stTextInput input, .stTextArea textarea, .stSelectbox select {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 10px !important;
        color: var(--text-primary) !important;
        font-family: 'Inter', sans-serif !important;
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: var(--accent-primary) !important;
        box-shadow: 0 0 15px var(--accent-glow) !important;
    }

    /* ---------- Tabs ---------- */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 10px !important;
        color: var(--text-secondary) !important;
        font-weight: 600 !important;
        padding: 8px 20px !important;
    }
    .stTabs [aria-selected="true"] {
        background: var(--accent-primary) !important;
        color: white !important;
        border-color: var(--accent-primary) !important;
    }

    /* ---------- Expander ---------- */
    .streamlit-expanderHeader {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 10px !important;
        color: var(--text-primary) !important;
        font-weight: 600 !important;
    }

    /* ---------- Dividers ---------- */
    hr {
        border-color: var(--border-subtle) !important;
        margin: 2rem 0 !important;
    }

    /* ---------- Metric ---------- */
    [data-testid="stMetric"] {
        background: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-radius: 14px;
        padding: 16px 20px;
    }
    [data-testid="stMetricLabel"] {
        color: var(--text-secondary) !important;
        font-weight: 600 !important;
    }
    [data-testid="stMetricValue"] {
        color: var(--text-primary) !important;
        font-weight: 800 !important;
    }

    /* ---------- Hide streamlit branding ---------- */
    #MainMenu, footer, header { visibility: hidden; }

    /* ---------- Scrollbar ---------- */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: var(--bg-primary); }
    ::-webkit-scrollbar-thumb {
        background: var(--accent-primary);
        border-radius: 3px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ------------------------------------------------------------------
# HTTP helpers
# ------------------------------------------------------------------


def _post(endpoint: str, payload: dict) -> dict | None:
    """POST to the FastAPI backend."""
    try:
        r = httpx.post(
            f"{API_BASE}{endpoint}",
            json=payload,
            timeout=TIMEOUT,
        )
        r.raise_for_status()
        return r.json()
    except httpx.ConnectError:
        st.error("⚠️ Cannot connect to the backend. Is `uvicorn app.main:app` running on port 8000?")
        return None
    except httpx.HTTPStatusError as e:
        st.error(f"API error {e.response.status_code}: {e.response.text}")
        return None
    except Exception as e:
        st.error(f"Request failed: {e}")
        return None


def _get(endpoint: str) -> dict | None:
    """GET from the FastAPI backend."""
    try:
        r = httpx.get(
            f"{API_BASE}{endpoint}",
            timeout=TIMEOUT,
        )
        r.raise_for_status()
        return r.json()
    except httpx.ConnectError:
        st.error("⚠️ Cannot connect to the backend. Is `uvicorn app.main:app` running on port 8000?")
        return None
    except httpx.HTTPStatusError as e:
        st.error(f"API error {e.response.status_code}: {e.response.text}")
        return None
    except Exception as e:
        st.error(f"Request failed: {e}")
        return None


# ------------------------------------------------------------------
# Sidebar
# ------------------------------------------------------------------

with st.sidebar:
    st.markdown('<p class="hero-badge">⚡ ET-Pulse</p>', unsafe_allow_html=True)
    st.markdown('<p class="hero-sub">AI-Native Business News Platform</p>', unsafe_allow_html=True)
    st.divider()

    page = st.radio(
        "Navigate",
        [
            "🏠 Dashboard",
            "📰 My ET",
            "🧭 News Navigator",
            "📈 Story Arc Tracker",
            "🌐 Vernacular Engine",
            "🎬 Video Studio",
        ],
        label_visibility="collapsed",
    )

    st.divider()
    st.markdown(
        '<div class="stat-pill">🟢 All systems operational</div>',
        unsafe_allow_html=True,
    )
    st.caption(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")


# ------------------------------------------------------------------
# Dashboard
# ------------------------------------------------------------------

if page == "🏠 Dashboard":
    st.markdown('<p class="hero-badge">Welcome to ET-Pulse</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="hero-sub">Your AI-powered command centre for Indian business news</p>',
        unsafe_allow_html=True,
    )
    st.write("")

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("📰 My ET", "Personalized")
    c2.metric("🧭 Navigator", "RAG Q&A")
    c3.metric("📈 Story Arc", "Sentiment")
    c4.metric("🌐 Vernacular", "10 Languages")
    c5.metric("🎬 Video", "AI Shorts")

    st.divider()

    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown(
            """
            <div class="glass-card">
                <h3>🚀 Quick Start</h3>
                <ol style="color: var(--text-secondary); line-height: 2;">
                    <li><strong>Ingest RSS</strong> — Go to <em>My ET</em> and click <strong>Ingest RSS Feeds</strong></li>
                    <li><strong>Ask Questions</strong> — Use <em>News Navigator</em> to query your knowledge base</li>
                    <li><strong>Track Stories</strong> — Analyze any company or sector in <em>Story Arc Tracker</em></li>
                    <li><strong>Translate</strong> — Convert articles to 10 Indian languages</li>
                    <li><strong>Generate Videos</strong> — Create AI news shorts in <em>Video Studio</em></li>
                </ol>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_r:
        st.markdown(
            """
            <div class="glass-card">
                <h3>🧠 Architecture</h3>
                <ul style="color: var(--text-secondary); line-height: 2;">
                    <li>📦 <strong>ChromaDB</strong> — Local vector store</li>
                    <li>🔤 <strong>sentence-transformers</strong> — Local embeddings</li>
                    <li>✨ <strong>Gemini Flash</strong> — RAG synthesis & scripts</li>
                    <li>⚡ <strong>Groq / Llama 3</strong> — Fast sentiment analysis</li>
                    <li>🗣️ <strong>IndicTrans2</strong> — Indian language translation</li>
                    <li>🎥 <strong>Google Veo</strong> — Video generation</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ------------------------------------------------------------------
# My ET — Personalized News
# ------------------------------------------------------------------

elif page == "📰 My ET":
    st.markdown('<p class="hero-badge">📰 My ET</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="hero-sub">Personalized news powered by semantic search</p>',
        unsafe_allow_html=True,
    )
    st.write("")

    tab1, tab2, tab3 = st.tabs(["🔄 Ingest RSS", "👤 Profile", "📖 Feed"])

    # ---- Ingest tab ----
    with tab1:
        st.markdown("Fetch live articles from Economic Times RSS feeds and index them into ChromaDB.")
        if st.button("⚡ Ingest RSS Feeds", key="ingest_rss"):
            with st.spinner("Fetching and embedding articles…"):
                result = _post("/my-et/ingest-rss", {})
            if result:
                st.success(f"✅ Ingested **{result['ingested_count']}** articles!")
                st.balloons()

    # ---- Profile tab ----
    with tab2:
        st.markdown("Create your interest profile for personalised feed ranking.")
        with st.form("profile_form"):
            user_id = st.text_input("User ID", value="user_001", placeholder="Enter user ID")
            interests = st.text_area(
                "Interests (one per line)",
                value="fintech\nIPO\nstartups\nRBI policy",
                height=120,
            )
            categories = st.multiselect(
                "Preferred Categories",
                ["Markets", "Economy", "Tech", "Banking", "Auto", "Pharma", "Energy"],
                default=["Markets", "Tech"],
            )
            submitted = st.form_submit_button("💾 Save Profile")

        if submitted:
            interests_list = [i.strip() for i in interests.strip().split("\n") if i.strip()]
            payload = {
                "user_id": user_id,
                "interests": interests_list,
                "preferred_categories": categories,
            }
            result = _post("/my-et/profile", payload)
            if result:
                st.success(f"✅ Profile saved for **{result['user_id']}**!")
                st.json(result)

    # ---- Feed tab ----
    with tab3:
        st.markdown("Retrieve your personalised news feed.")
        col_a, col_b = st.columns([3, 1])
        with col_a:
            feed_user_id = st.text_input("User ID", value="user_001", key="feed_uid")
        with col_b:
            top_k = st.number_input("Articles", min_value=1, max_value=50, value=10)

        if st.button("📖 Get My Feed", key="get_feed"):
            with st.spinner("Searching for your personalised articles…"):
                result = _get(f"/my-et/feed/{feed_user_id}?top_k={top_k}")
            if result:
                st.markdown(f'<div class="stat-pill">📊 {result["total_results"]} articles found</div>', unsafe_allow_html=True)
                st.write("")
                for i, article in enumerate(result.get("articles", []), 1):
                    with st.expander(f"**{i}. {article['title'][:80]}**", expanded=(i <= 3)):
                        st.markdown(f"**Source:** {article.get('source', 'N/A')}  •  **Category:** {article.get('category', 'N/A')}")
                        st.write(article.get("summary", ""))
                        if article.get("url"):
                            st.markdown(f"[Read full article →]({article['url']})")


# ------------------------------------------------------------------
# News Navigator — RAG Q&A
# ------------------------------------------------------------------

elif page == "🧭 News Navigator":
    st.markdown('<p class="hero-badge">🧭 News Navigator</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="hero-sub">Ask anything about business news — powered by RAG + Gemini Flash</p>',
        unsafe_allow_html=True,
    )
    st.write("")

    question = st.text_area(
        "Your question",
        placeholder="e.g. What are the latest developments in Indian fintech regulations?",
        height=100,
    )
    col_q1, col_q2 = st.columns([1, 4])
    with col_q1:
        nav_top_k = st.number_input("Sources", min_value=1, max_value=20, value=5, key="nav_k")

    if st.button("🔍 Ask Navigator", key="ask_nav", disabled=not question.strip()):
        with st.spinner("Retrieving articles & synthesizing answer…"):
            result = _post("/navigator/query", {"question": question, "top_k": nav_top_k})

        if result:
            # Answer section
            st.markdown("### 💡 Answer")
            st.markdown(
                f'<div class="glass-card">{result["answer"]}</div>',
                unsafe_allow_html=True,
            )

            # Sources section
            sources = result.get("sources", [])
            if sources:
                st.markdown(f"### 📚 Sources ({len(sources)})")
                for s in sources:
                    score_pct = round(s["relevance_score"] * 100, 1)
                    color = "var(--success)" if score_pct > 70 else ("var(--warning)" if score_pct > 40 else "var(--danger)")
                    st.markdown(
                        f"""<div class="glass-card" style="padding: 14px 20px;">
                            <strong>{s['title']}</strong>
                            <span style="float: right; color: {color}; font-weight: 700;">{score_pct}% match</span>
                        </div>""",
                        unsafe_allow_html=True,
                    )

            st.caption(f"Model: {result.get('model_used', 'N/A')}")


# ------------------------------------------------------------------
# Story Arc Tracker
# ------------------------------------------------------------------

elif page == "📈 Story Arc Tracker":
    st.markdown('<p class="hero-badge">📈 Story Arc Tracker</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="hero-sub">Timeline & sentiment analysis powered by Groq / Llama 3</p>',
        unsafe_allow_html=True,
    )
    st.write("")

    col_t1, col_t2 = st.columns([3, 1])
    with col_t1:
        topic = st.text_input("Topic or entity", placeholder="e.g. Reliance Industries, RBI, Tata Motors")
    with col_t2:
        arc_top_k = st.number_input("Articles", min_value=1, max_value=50, value=10, key="arc_k")

    if st.button("📊 Analyze Story Arc", key="analyze_arc", disabled=not topic.strip()):
        with st.spinner("Analyzing with Groq / Llama 3 …"):
            result = _post("/story-arc/analyze", {"topic": topic, "top_k": arc_top_k})

        if result:
            # Sentiment overview
            sa = result.get("sentiment_analysis", {})
            st.markdown("### 🎯 Sentiment Overview")

            s1, s2, s3, s4 = st.columns(4)
            sentiment = sa.get("overall_sentiment", "neutral")
            sentiment_emoji = {"positive": "🟢", "negative": "🔴", "neutral": "🟡", "mixed": "🟣"}.get(sentiment, "⚪")
            s1.metric("Overall", f"{sentiment_emoji} {sentiment.title()}")
            s2.metric("Confidence", f"{round(sa.get('confidence', 0) * 100)}%")
            s3.metric("Positive", f"{round(sa.get('positive_ratio', 0) * 100)}%")
            s4.metric("Negative", f"{round(sa.get('negative_ratio', 0) * 100)}%")

            # Sentiment donut chart
            fig = go.Figure(
                data=[go.Pie(
                    labels=["Positive", "Negative", "Neutral"],
                    values=[
                        sa.get("positive_ratio", 0.33),
                        sa.get("negative_ratio", 0.33),
                        sa.get("neutral_ratio", 0.34),
                    ],
                    hole=0.6,
                    marker=dict(colors=["#00e676", "#ff5252", "#ffab40"]),
                    textfont=dict(color="white", size=13),
                )]
            )
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#eaeaff", family="Inter"),
                showlegend=True,
                legend=dict(font=dict(color="#9d9db5")),
                height=300,
                margin=dict(t=20, b=20, l=20, r=20),
            )
            st.plotly_chart(fig, use_container_width=True)

            # Timeline
            timeline = result.get("timeline", [])
            if timeline:
                st.markdown(f"### 📅 Timeline ({len(timeline)} events)")
                for i, ev in enumerate(timeline, 1):
                    sent = ev.get("sentiment", "neutral")
                    css_class = f"sentiment-{sent}"
                    sig = round(ev.get("significance_score", 0.5) * 100)
                    st.markdown(
                        f"""<div class="glass-card">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <strong style="font-size: 1rem;">{ev['headline']}</strong>
                                <span class="{css_class}" style="text-transform: uppercase; font-size: 0.75rem;">{sent}</span>
                            </div>
                            <p style="color: var(--text-secondary); margin: 8px 0 4px 0;">{ev['summary']}</p>
                            <div style="display: flex; gap: 16px; font-size: 0.8rem; color: var(--text-muted);">
                                <span>📅 {ev['date']}</span>
                                <span>⚡ Significance: {sig}%</span>
                            </div>
                        </div>""",
                        unsafe_allow_html=True,
                    )

            st.caption(f"Analyzed {result.get('article_count', 0)} articles  •  Model: {result.get('model_used', 'N/A')}")


# ------------------------------------------------------------------
# Vernacular Engine
# ------------------------------------------------------------------

elif page == "🌐 Vernacular Engine":
    st.markdown('<p class="hero-badge">🌐 Vernacular Engine</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="hero-sub">Culturally adapted translations via AI4Bharat IndicTrans2</p>',
        unsafe_allow_html=True,
    )
    st.write("")

    LANG_MAP = {
        "🇮🇳 Hindi": "hi",
        "🇮🇳 Tamil": "ta",
        "🇮🇳 Telugu": "te",
        "🇮🇳 Bengali": "bn",
        "🇮🇳 Marathi": "mr",
        "🇮🇳 Gujarati": "gu",
        "🇮🇳 Kannada": "kn",
        "🇮🇳 Malayalam": "ml",
        "🇮🇳 Punjabi": "pa",
        "🇮🇳 Odia": "or",
    }

    text_to_translate = st.text_area(
        "English text to translate",
        placeholder="Paste a news article or paragraph here…",
        height=150,
    )

    target_lang_display = st.selectbox("Target Language", list(LANG_MAP.keys()))
    target_lang_code = LANG_MAP[target_lang_display]

    if st.button("🌐 Translate", key="translate_btn", disabled=not text_to_translate.strip()):
        with st.spinner(f"Translating to {target_lang_display}…"):
            result = _post(
                "/vernacular/translate",
                {"text": text_to_translate, "target_language": target_lang_code},
            )

        if result:
            st.markdown("### ✅ Translation")
            col_orig, col_trans = st.columns(2)
            with col_orig:
                st.markdown(
                    f"""<div class="glass-card">
                        <h4 style="color: var(--text-muted); margin-bottom: 8px;">🇬🇧 English</h4>
                        <p style="color: var(--text-primary); line-height: 1.7;">{result['original_text']}</p>
                    </div>""",
                    unsafe_allow_html=True,
                )
            with col_trans:
                st.markdown(
                    f"""<div class="glass-card" style="border-color: var(--accent-primary);">
                        <h4 style="color: var(--accent-primary); margin-bottom: 8px;">{target_lang_display}</h4>
                        <p style="color: var(--text-primary); line-height: 1.7; font-size: 1.1rem;">{result['translated_text']}</p>
                    </div>""",
                    unsafe_allow_html=True,
                )

            engine = result.get("engine", "unknown")
            engine_label = "IndicTrans2" if engine == "indictrans2" else "Gemini (fallback)"
            st.caption(f"Engine: {engine_label}")


# ------------------------------------------------------------------
# AI News Video Studio
# ------------------------------------------------------------------

elif page == "🎬 Video Studio":
    st.markdown('<p class="hero-badge">🎬 Video Studio</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="hero-sub">Generate 60–120s AI news shorts with Gemini + Veo</p>',
        unsafe_allow_html=True,
    )
    st.write("")

    tab_gen, tab_status = st.tabs(["🎬 Generate", "🔍 Check Status"])

    with tab_gen:
        with st.form("video_form"):
            v_title = st.text_input("Article Title", placeholder="e.g. RBI Holds Repo Rate Steady at 6.5%")
            v_content = st.text_area(
                "Article Content",
                placeholder="Paste the full article text here…",
                height=180,
            )
            v_col1, v_col2 = st.columns(2)
            with v_col1:
                v_duration = st.slider("Duration (seconds)", 60, 120, 90)
            with v_col2:
                v_style = st.selectbox(
                    "Visual Style",
                    ["professional_news", "data_driven", "storytelling", "breaking_news"],
                )
            v_submit = st.form_submit_button("🎬 Generate Video")

        if v_submit and v_title.strip() and v_content.strip():
            with st.spinner("Generating script & requesting video…"):
                result = _post(
                    "/video-studio/generate",
                    {
                        "article_title": v_title,
                        "article_content": v_content,
                        "duration_seconds": v_duration,
                        "style": v_style,
                    },
                )

            if result:
                status = result.get("status", "unknown")
                gen_id = result.get("generation_id", "")

                if status == "script_only":
                    st.warning("⚠️ Veo API unavailable — script generated successfully.")
                elif status == "processing":
                    st.info(f"🎬 Video generation started! Poll ID: `{gen_id}`")
                else:
                    st.success(f"Status: **{status}** — ID: `{gen_id}`")

                # Show script
                script = result.get("script")
                if script:
                    st.markdown("### 📝 Generated Script")
                    st.markdown(
                        f"""<div class="glass-card">
                            <h4 style="color: var(--accent-primary);">🎙️ Narration</h4>
                            <p style="color: var(--text-primary); line-height: 1.8;">{script['narration']}</p>
                        </div>""",
                        unsafe_allow_html=True,
                    )

                    visuals = script.get("visual_descriptions", [])
                    if visuals:
                        st.markdown("#### 🎨 Visual Scenes")
                        for j, vis in enumerate(visuals, 1):
                            st.markdown(
                                f"""<div class="glass-card" style="padding: 12px 18px;">
                                    <span style="color: var(--accent-primary); font-weight: 700;">Scene {j}:</span>
                                    <span style="color: var(--text-secondary);"> {vis}</span>
                                </div>""",
                                unsafe_allow_html=True,
                            )

                    st.caption(f"Estimated duration: {script.get('duration_estimate_seconds', v_duration)}s")

    with tab_status:
        st.markdown("Poll the status of a previously submitted video generation request.")
        poll_id = st.text_input("Generation ID", placeholder="Paste the generation ID here")
        if st.button("🔄 Check Status", key="poll_status", disabled=not poll_id.strip()):
            with st.spinner("Polling…"):
                result = _get(f"/video-studio/status/{poll_id}")
            if result:
                status = result.get("status", "unknown")
                status_colors = {
                    "completed": "var(--success)",
                    "processing": "var(--warning)",
                    "failed": "var(--danger)",
                    "pending": "var(--text-muted)",
                    "script_only": "var(--accent-primary)",
                }
                color = status_colors.get(status, "var(--text-secondary)")
                st.markdown(
                    f"""<div class="glass-card">
                        <strong>Status:</strong>
                        <span style="color: {color}; font-weight: 700; text-transform: uppercase;">{status}</span>
                        <br/><br/>
                        <strong>Message:</strong> {result.get('message', 'N/A')}
                    </div>""",
                    unsafe_allow_html=True,
                )
                if result.get("video_url"):
                    st.markdown(f"🎥 **[Download Video]({result['video_url']})**")
