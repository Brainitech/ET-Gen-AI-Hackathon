"""
My ET — The Personalized Newsroom
Standalone Streamlit frontend | ET Hackathon Round 2
ET-inspired dark red theme | 4 personas | Live RSS + AI snippets
"""

import streamlit as st
import requests
import time
import uuid

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="My ET — Your Personalized Newsroom",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="collapsed",
)

API_BASE = "http://localhost:8000/api/v1"

# ── ET Dark Red Design System ──────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;800&family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Base ── */
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp {
    background: #0d0d0d;
    color: #e8e0d5;
}

/* ── ET Header Bar ── */
.et-header {
    background: linear-gradient(135deg, #8B0000 0%, #B22222 50%, #8B0000 100%);
    padding: 0.75rem 2rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 3px solid #FF4444;
    margin: -1rem -1rem 2rem -1rem;
}
.et-logo {
    font-family: 'Playfair Display', serif;
    font-size: 1.8rem;
    font-weight: 800;
    color: #FFFFFF;
    letter-spacing: -0.02em;
}
.et-logo span { color: #FFD700; }
.et-tagline {
    color: rgba(255,255,255,0.75);
    font-size: 0.78rem;
    font-weight: 500;
    letter-spacing: 0.15em;
    text-transform: uppercase;
}

/* ── Persona Switcher ── */
.persona-bar {
    display: flex;
    gap: 0.75rem;
    background: #1a1a1a;
    border: 1px solid #2a2a2a;
    border-radius: 12px;
    padding: 0.5rem;
    margin-bottom: 1.5rem;
}
.persona-chip {
    flex: 1;
    text-align: center;
    padding: 0.6rem 1rem;
    border-radius: 8px;
    cursor: pointer;
    font-size: 0.85rem;
    font-weight: 500;
    color: #888;
    border: 1px solid transparent;
    transition: all 0.2s;
}
.persona-chip.active {
    background: linear-gradient(135deg, #8B0000, #B22222);
    color: #fff;
    border-color: #FF4444;
    box-shadow: 0 0 15px rgba(178,34,34,0.4);
}

/* ── Profile Form ── */
.profile-container {
    max-width: 640px;
    margin: 0 auto;
    padding: 2rem 0;
}
.profile-heading {
    font-family: 'Playfair Display', serif;
    font-size: 2.2rem;
    font-weight: 700;
    color: #FFFFFF;
    line-height: 1.2;
    margin-bottom: 0.5rem;
}
.profile-sub {
    color: #888;
    font-size: 0.95rem;
    margin-bottom: 2rem;
}

/* ── Persona Cards (onboarding) ── */
.persona-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
    margin-bottom: 2rem;
}
.persona-card {
    background: #1a1a1a;
    border: 2px solid #2a2a2a;
    border-radius: 14px;
    padding: 1.5rem;
    cursor: pointer;
    transition: all 0.2s;
    text-align: center;
}
.persona-card:hover { border-color: #8B0000; }
.persona-card.selected {
    border-color: #B22222;
    background: rgba(139,0,0,0.12);
    box-shadow: 0 0 20px rgba(178,34,34,0.2);
}
.persona-icon { font-size: 2.2rem; margin-bottom: 0.5rem; }
.persona-name {
    font-weight: 700;
    font-size: 1rem;
    color: #fff;
    margin-bottom: 0.25rem;
}
.persona-desc { color: #666; font-size: 0.8rem; line-height: 1.5; }

/* ── News Cards ── */
.news-card {
    background: #141414;
    border: 1px solid #222;
    border-left: 4px solid #8B0000;
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1rem;
    transition: border-color 0.2s, box-shadow 0.2s;
}
.news-card:hover {
    border-color: #B22222;
    box-shadow: 0 4px 20px rgba(139,0,0,0.15);
}
.news-meta {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 0.5rem;
}
.news-source {
    font-size: 0.72rem;
    font-weight: 700;
    color: #B22222;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}
.news-time { color: #555; font-size: 0.72rem; }
.news-title {
    font-size: 1.05rem;
    font-weight: 600;
    color: #e8e0d5;
    line-height: 1.4;
    margin-bottom: 0.5rem;
}
.news-summary { color: #666; font-size: 0.85rem; line-height: 1.6; margin-bottom: 0.75rem; }

/* ── AI Snippet ── */
.ai-snippet {
    background: rgba(139,0,0,0.08);
    border: 1px solid rgba(178,34,34,0.25);
    border-radius: 8px;
    padding: 0.75rem 1rem;
    margin-top: 0.75rem;
}
.ai-snippet-label {
    font-size: 0.68rem;
    font-weight: 700;
    color: #B22222;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-bottom: 0.3rem;
}
.ai-snippet-text { color: #ccc; font-size: 0.88rem; line-height: 1.6; }

/* ── Tags ── */
.tag {
    display: inline-block;
    background: #1e1e1e;
    border: 1px solid #2a2a2a;
    color: #888;
    font-size: 0.7rem;
    font-weight: 500;
    padding: 0.2rem 0.6rem;
    border-radius: 999px;
    margin-right: 0.35rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}

/* ── Sentiment dots ── */
.dot-positive { color: #4ade80; }
.dot-negative { color: #f87171; }
.dot-neutral  { color: #888; }

/* ── Deep Dive Modal ── */
.deep-dive-section {
    background: #1a1a1a;
    border: 1px solid #2a2a2a;
    border-radius: 10px;
    padding: 1rem 1.25rem;
    margin-bottom: 0.75rem;
}
.deep-dive-heading {
    font-size: 0.8rem;
    font-weight: 700;
    color: #B22222;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 0.4rem;
}
.deep-dive-content { color: #ccc; font-size: 0.9rem; line-height: 1.7; }
.bottom-line {
    background: linear-gradient(135deg, rgba(139,0,0,0.2), rgba(178,34,34,0.1));
    border: 1px solid rgba(178,34,34,0.4);
    border-radius: 10px;
    padding: 1rem 1.25rem;
    margin-top: 1rem;
}
.bottom-line-label {
    font-size: 0.72rem;
    font-weight: 700;
    color: #FFD700;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-bottom: 0.3rem;
}
.bottom-line-text {
    color: #fff;
    font-size: 0.95rem;
    font-weight: 500;
    line-height: 1.5;
}

/* ── Section headings ── */
.section-label {
    font-size: 0.72rem;
    font-weight: 700;
    color: #555;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #1e1e1e;
}

/* ── Streamlit overrides ── */
.stButton>button {
    background: linear-gradient(135deg, #8B0000, #B22222) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-family: 'Inter', sans-serif !important;
    transition: opacity 0.2s !important;
}
.stButton>button:hover { opacity: 0.85 !important; }
.stTextInput input, .stTextArea textarea, .stSelectbox select, .stMultiSelect [data-baseweb] {
    background: #1a1a1a !important;
    border-color: #2a2a2a !important;
    color: #e8e0d5 !important;
    border-radius: 8px !important;
}
div[data-testid="stRadio"] label { color: #aaa !important; }
.stSpinner { color: #B22222 !important; }
.stMetric { background: #141414; border: 1px solid #222; border-radius: 10px; padding: 0.75rem; }

/* ── Scrollable feed ── */
.feed-container { max-height: 80vh; overflow-y: auto; padding-right: 0.5rem; }
</style>
""", unsafe_allow_html=True)


# ── Helpers ────────────────────────────────────────────────────────────────────

def api_post(endpoint: str, payload: dict):
    try:
        r = requests.post(f"{API_BASE}{endpoint}", json=payload, timeout=120)
        r.raise_for_status()
        return r.json(), None
    except requests.exceptions.ConnectionError:
        return None, "❌ Cannot reach backend. Run `uvicorn app.main:app --reload`"
    except requests.exceptions.HTTPError as e:
        try:
            detail = e.response.json().get("detail", str(e))
        except Exception:
            detail = str(e)
        return None, f"API Error: {detail}"
    except Exception as e:
        return None, str(e)

def _get_default_interests(persona: str) -> list[str]:
    defaults = {
        "investor":  ["markets", "sensex", "nifty", "stocks", "rbi", "sebi"],
        "founder":   ["startup", "funding", "venture capital", "unicorn", "series"],
        "student":   ["economy", "budget", "policy", "rbi", "gdp", "career"],
        "executive": ["corporate", "policy", "merger", "regulation", "strategy", "industry"],
    }
    return defaults.get(persona, ["business", "economy"])

def api_get(endpoint: str, params: dict = None):
    try:
        r = requests.get(f"{API_BASE}{endpoint}", params=params, timeout=120)
        r.raise_for_status()
        return r.json(), None
    except requests.exceptions.ConnectionError:
        return None, "❌ Cannot reach backend."
    except Exception as e:
        return None, str(e)


def sentiment_dot(sentiment: str) -> str:
    if sentiment == "positive":
        return '<span class="dot-positive">▲</span>'
    elif sentiment == "negative":
        return '<span class="dot-negative">▼</span>'
    return '<span class="dot-neutral">●</span>'


def render_tags(tags: list) -> str:
    return "".join(f'<span class="tag">{t}</span>' for t in tags[:4])


# ── ET Header ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="et-header">
    <div class="et-logo">My<span>ET</span></div>
    <div class="et-tagline">Your Personalized Newsroom · AI-Powered</div>
</div>
""", unsafe_allow_html=True)


# ── Session State ──────────────────────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "onboarding"
if "user_id" not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())
if "profile" not in st.session_state:
    st.session_state.profile = {}
if "persona" not in st.session_state:
    st.session_state.persona = None
if "briefing" not in st.session_state:
    st.session_state.briefing = None
if "deep_dive_article" not in st.session_state:
    st.session_state.deep_dive_article = None


# ══════════════════════════════════════════════════════════════════════════════
# ONBOARDING — Profile Setup
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "onboarding":

    st.markdown('<div class="profile-container">', unsafe_allow_html=True)
    st.markdown("""
    <div class="profile-heading">Who are you reading<br>the news as?</div>
    <div class="profile-sub">Tell us your role. We'll make ET make sense for <em>your</em> world.</div>
    """, unsafe_allow_html=True)

    # ── Persona selector ──
    PERSONAS = {
        "investor":  {"icon": "📈", "name": "Investor", "desc": "Track markets, MFs, stocks & portfolio impact"},
        "founder":   {"icon": "🚀", "name": "Founder",  "desc": "Funding news, competitor moves & ecosystem shifts"},
        "student":   {"icon": "🎓", "name": "Student",  "desc": "Plain-English explainers, career-relevant context"},
        "executive": {"icon": "🏢", "name": "Executive","desc": "Strategy, industry trends & policy implications"},
    }

    cols = st.columns(4)
    for i, (key, meta) in enumerate(PERSONAS.items()):
        with cols[i]:
            selected = st.session_state.persona == key
            card_cls = "persona-card selected" if selected else "persona-card"
            st.markdown(f"""
            <div class="{card_cls}" onclick="">
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

        # ── Dynamic context form ──────────────────────────────────────────────
        if p == "investor":
            name = st.text_input("Your name (optional)", placeholder="e.g. Ravi")
            sectors = st.multiselect(
                "Sectors you invest in",
                ["Banking", "IT", "Pharma", "Auto", "FMCG", "Real Estate", "Energy", "Metals", "Telecom"],
                default=["Banking", "IT"],
            )
            stocks = st.text_input(
                "Stocks / MFs you track (comma separated)",
                placeholder="HDFC Bank, Nifty 50, Axis Bluechip Fund",
            )
            col1, col2 = st.columns(2)
            with col1:
                style = st.selectbox("Investment style", ["long-term", "short-term", "swing-trader", "SIP"])
            with col2:
                risk = st.selectbox("Risk appetite", ["conservative", "moderate", "aggressive"])

            profile_data.update({
                "name": name,
                "interests": [s.lower() for s in sectors] + ["markets", "sensex", "stocks"],
                "investor_context": {
                    "portfolio_sectors": [s.lower() for s in sectors],
                    "tracked_stocks": [s.strip() for s in stocks.split(",") if s.strip()],
                    "investment_style": style,
                    "risk_appetite": risk,
                },
            })

        elif p == "founder":
            name = st.text_input("Your name (optional)", placeholder="e.g. Priya")
            sector = st.text_input("Your startup sector", placeholder="e.g. Fintech, Edtech, D2C")
            col1, col2 = st.columns(2)
            with col1:
                stage = st.selectbox("Stage", ["idea", "early", "seed", "series-a", "series-b", "growth"])
            with col2:
                fundraising = st.selectbox("Fundraising status", ["not-raising", "actively-raising", "closing-round"])
            competitors = st.text_input(
                "Competitors to watch (comma separated)",
                placeholder="e.g. Zepto, Blinkit, Swiggy Instamart",
            )

            profile_data.update({
                "name": name,
                "interests": [sector.lower(), "startup", "funding", "venture capital", "ipo"],
                "founder_context": {
                    "startup_sector": sector,
                    "stage": stage,
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
                "student_context": {
                    "field_of_study": field,
                    "career_goal": goal,
                    "knowledge_level": level,
                },
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
                    "industry": industry,
                    "function": function,
                    "company_size": size,
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
                    st.session_state.page = "feed"
                    st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# FEED — Personalized News Cards
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "feed":

    profile  = st.session_state.profile
    persona  = st.session_state.persona
    user_id  = st.session_state.user_id

    PERSONA_META = {
        "investor":  {"icon": "📈", "name": "Investor"},
        "founder":   {"icon": "🚀", "name": "Founder"},
        "student":   {"icon": "🎓", "name": "Student"},
        "executive": {"icon": "🏢", "name": "Executive"},
    }

    # ── Top bar ────────────────────────────────────────────────────────────────
    col_greeting, col_refresh, col_switch = st.columns([5, 1, 1])
    with col_greeting:
        name = profile.get("name", "").strip()
        greeting = f"Good morning, {name}! 👋" if name else "Good morning! 👋"
        meta = PERSONA_META.get(persona, {})
        st.markdown(f"""
        <div>
            <div style="font-family:'Playfair Display',serif; font-size:1.6rem; font-weight:700; color:#fff; margin-bottom:0.2rem;">
                {greeting}
            </div>
            <div style="color:#666; font-size:0.85rem;">
                {meta.get('icon','')} Your <b style="color:#B22222">{meta.get('name','')} Newsroom</b> · Live from Economic Times
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col_refresh:
        if st.button("↻ Refresh", use_container_width=True):
            st.session_state.briefing = None
            st.rerun()
    with col_switch:
        if st.button("← Switch", use_container_width=True):
            st.session_state.page = "onboarding"
            st.session_state.briefing = None
            st.session_state.persona = None
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Persona switcher (demo hero) ───────────────────────────────────────────
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
                    # Switch persona — keep same user_id, post new profile
                    st.session_state.persona = key
                    new_profile = {"persona_type": key, "user_id": user_id, "interests": (key)}
                    api_post("/my-et/profile/extended", new_profile)
                    st.session_state.briefing = None
                    st.session_state.profile = new_profile
                    st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Load briefing ──────────────────────────────────────────────────────────
    if st.session_state.briefing is None:
        with st.spinner("⚡ Fetching live ET news & generating your AI insights…"):
            data, err = api_get(f"/my-et/briefing/{user_id}", {"top_n": 5})
            if err:
                st.error(err)
                st.stop()
            st.session_state.briefing = data

    briefing = st.session_state.briefing
    articles = briefing.get("articles", [])

    # ── Stats bar ─────────────────────────────────────────────────────────────
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("📰 Articles", briefing.get("total_articles", 0))
    with m2:
        st.metric("⚡ AI Insights", briefing.get("enriched_count", 0))
    with m3:
        st.metric("🎭 Persona", PERSONA_META.get(persona, {}).get("name", ""))
    with m4:
        positive = sum(1 for a in articles if a.get("sentiment") == "positive")
        st.metric("📊 Positive News", f"{positive}/{len(articles)}")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-label">📰 Your Feed</div>', unsafe_allow_html=True)

    # ── Deep Dive Modal ────────────────────────────────────────────────────────
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
                sections = dd_data.get("sections", [])
                for i, section in enumerate(sections):
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

    # ── News Cards ────────────────────────────────────────────────────────────
    for i, art in enumerate(articles):
        title    = art.get("title", "Untitled")
        summary  = art.get("summary", "")[:220]
        source   = art.get("source", "ET")
        pub      = art.get("published", "")[:16]
        snippet  = art.get("persona_snippet", "")
        ready    = art.get("snippet_ready", False)
        sentiment = art.get("sentiment", "neutral")
        tags     = art.get("tags", [])
        link     = art.get("link", "")

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

        # Action buttons
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
