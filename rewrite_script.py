import re

with open('/Users/ajiteshdwivedi/Downloads/ET-Gen-AI-Hackathon-brainiac/streamlit_app.py', 'r') as f:
    text = f.read()

new_css = """<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;800&family=Inter:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: #fdfdfd; color: #111; }
header[data-testid="stHeader"] { display: none; }
.top-ticker { background: #111; color: #fff; padding: 0.35rem 2rem; font-size: 0.75rem; display: flex; align-items: center; font-weight: 500; margin: -1rem -4rem 1rem -4rem; }
.et-header-light { padding: 1rem 0; display: flex; align-items: center; justify-content: space-between; border-bottom: 2px solid #ef4444; margin-bottom: 1.5rem; }
.et-logo-light { font-family: 'Playfair Display', serif; font-size: 3.5rem; font-weight: 800; color: #ef4444; line-height: 1; margin-bottom: -4px; }
.et-tagline-light { color: #555; font-size: 0.8rem; font-weight: 700; letter-spacing: 0.15em; text-transform: uppercase; margin-top: 4px; }
.hero-banner { background: #f9fafb; border: 1px solid #e5e7eb; border-left: 5px solid #ef4444; border-radius: 8px; padding: 2rem; margin-bottom: 2rem; }
.hero-title { font-family: 'Playfair Display', serif; font-size: 2.2rem; font-weight: 800; color: #111; margin: 0; }
.hero-sub { color: #555; font-size: 1rem; margin-top: 0.6rem; }
.glass-card { background: #fff; border: 1px solid #e5e7eb; border-radius: 8px; padding: 1.5rem; margin-bottom: 1rem; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
.section-heading { display: flex; align-items: center; gap: 0.6rem; font-size: 0.8rem; font-weight: 700; color: #111; text-transform: uppercase; margin: 1.5rem 0 1rem; padding: 0.5rem 1rem; background: #f9fafb; border-left: 3px solid #ef4444; border-radius: 0 4px 4px 0; }
.section-label { font-size: 0.75rem; font-weight: 700; color: #111; text-transform: uppercase; margin-bottom: 1rem; padding-bottom: 0.5rem; border-bottom: 1px solid #e5e7eb; }
.news-card { background: #fff; border: 1px solid #e5e7eb; border-top: 4px solid #ef4444; border-radius: 8px; padding: 1.5rem; margin-bottom: 1rem; box-shadow: 0 2px 8px rgba(0,0,0,0.04); }
.news-meta { display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.5rem; }
.news-source { font-size: 0.7rem; font-weight: 700; color: #ef4444; text-transform: uppercase; }
.news-time { color: #666; font-size: 0.7rem; }
.news-title { font-size: 1.4rem; font-family: 'Playfair Display', serif; font-weight: 800; color: #111; line-height: 1.3; margin-bottom: 0.5rem; }
.news-summary { color: #333; font-size: 0.95rem; line-height: 1.6; margin-bottom: 0.75rem; }
div[data-testid="stRadio"] > div { flex-direction: row; gap: 2rem; border-bottom: 2px solid #000; padding-bottom: 0; margin-bottom: 1rem; }
div[data-testid="stRadio"] label { padding: 0.8rem 0; cursor: pointer !important; margin: 0; }
div[data-testid="stRadio"] label > div:first-child { display: none; }
div[data-testid="stRadio"] label > div:last-child { font-weight: 700 !important; font-size: 0.85rem !important; color: #888 !important; text-transform: uppercase !important; }
div[data-testid="stRadio"] label[data-checked="true"] { border-bottom: 3px solid #ef4444; }
div[data-testid="stRadio"] label[data-checked="true"] > div:last-child { color: #ef4444 !important; }
.stMetric { background: #fff; border: 1px solid #e5e7eb; border-top: 2px solid #111; border-radius: 6px; padding: 1rem; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
.persona-card { background: #fff; border: 2px solid #e5e7eb; border-radius: 12px; padding: 1.5rem; text-align: center; cursor: pointer; }
.persona-card.selected { border-color: #ef4444; background: #fef2f2; }
.persona-name { font-weight: 700; font-size: 1rem; color: #111; margin-bottom: 0.25rem; }
.persona-desc { color: #555; font-size: 0.8rem; line-height: 1.5; }
.ai-snippet { background: #fafafa; border: 1px solid #e5e7eb; border-left: 3px solid #d97706; border-radius: 6px; padding: 0.85rem 1rem; margin-top: 0.85rem; }
.ai-snippet-label { font-size: 0.65rem; font-weight: 700; color: #d97706; text-transform: uppercase; margin-bottom: 0.35rem; }
.ai-snippet-text { color: #333; font-size: 0.9rem; line-height: 1.6; font-style: italic; }
.stButton>button { background: #fff !important; color: #333 !important; border: 1px solid #d1d5db !important; border-radius: 6px !important; font-weight: 600 !important; }
.stButton>button:hover { background: #f3f4f6 !important; border-color: #9ca3af !important; }
.deep-dive-section { background: #f9fafb; border: 1px solid #e5e7eb; border-left: 3px solid #ef4444; border-radius: 6px; padding: 1rem; margin-bottom: 0.75rem; color: #111; }
.deep-dive-heading { font-weight: 700; color: #ef4444; margin-bottom: 0.4rem; font-size:0.85rem; }
.deep-dive-content { color:#333; font-size:0.9rem; }
.bottom-line { background:#fef3c7; border: 1px solid #fcd34d; border-radius: 6px; padding: 1rem; color:#92400e; margin-top:1rem; }
.bottom-line-label { font-size:0.75rem; font-weight:700; color:#b45309; text-transform:uppercase; margin-bottom:0.3rem;}
.gloss-card { background:#fff; border:1px solid #e5e7eb; border-left:3px solid #8b5cf6; border-radius:6px; padding:0.75rem; color:#111; }
.gloss-term { font-weight:700; color:#7c3aed; font-size:0.9rem; }
.err-box { background: #fee2e2; border: 1px solid #fecaca; border-radius: 6px; padding: 1rem; color: #b91c1c; }
.info-box { background: #f3f4f6; border: 1px solid #e5e7eb; border-radius: 6px; padding: 1rem; color: #333; }
.tag { background: #f3f4f6; border: 1px solid #e5e7eb; color: #555; font-size: 0.7rem; font-weight: 600; padding: 0.2rem 0.6rem; border-radius: 999px; }
.dot-positive { color: #10b981; } .dot-negative { color: #ef4444; } .dot-neutral { color: #94a3b8; }
.badge-positive { background: #dcfce7; color: #15803d; border: 1px solid #bbf7d0; padding:2px 8px; border-radius:12px; font-size:0.75rem;}
.badge-negative { background: #fee2e2; color: #b91c1c; border: 1px solid #fecaca; padding:2px 8px; border-radius:12px; font-size:0.75rem;}
.timeline-dot { width:10px; height:10px; border-radius:50%; background:#ef4444; margin-top:5px; box-shadow:0 0 0 3px #fee2e2; }
.player-card { background:#fff; border:1px solid #e5e7eb; border-left: 3px solid #ef4444; padding:1rem; border-radius:6px; margin-bottom:0.5rem;}
.stTextInput input, .stTextArea textarea, .stSelectbox select { background:#fff!important; color:#111!important; border-color:#d1d5db!important; }
</style>
"""

# 1. Replace CSS block
text = re.sub(r'<style>.*?</style>', new_css, text, flags=re.DOTALL)

# 2. Extract Sidebar
old_sidebar = '''# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding: 1.25rem 0 1rem; text-align:center; border-bottom: 1px solid #1a1a1a; margin-bottom: 1rem;">
        <div style="font-family:'Playfair Display',serif; font-size:2rem; font-weight:800; color:#FFFFFF; letter-spacing:-0.02em; line-height:1;">
            aether<span style="color:#B22222;">_ai</span>
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

    st.markdown("---")'''


new_top_level = '''
# ── Global ET Header ──
st.markdown("""
<div class="top-ticker">
    <span style="color:#4ade80;">312.40 (+0.43%)</span> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 
    <span style="color:#f59e0b;">NIFTY 50</span> 22,197.90 <span style="color:#4ade80;">▲ 98.15 (+0.44%)</span> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
    <span style="color:#f59e0b;">USD/INR</span> 83.74 <span style="color:#ef4444;">▼ 0.12</span> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
    <span style="color:#f59e0b;">GOLD</span> ₹69,840 <span style="color:#4ade80;">▲ 210 (+0.30%)</span>
</div>
<div class="et-header-light">
    <div>
        <div class="et-logo-light">ET</div>
        <div class="et-tagline-light">ECONOMIC TIMES INTELLIGENCE</div>
        <div style="margin-top:8px;"><span style="background:#111; color:#fff; font-size:0.75rem; font-weight:600; padding:4px 8px; border-radius:4px;">● AI-Powered Newsroom · Live</span></div>
    </div>
    <div style="display:flex; gap:2.5rem; align-items:center;">
        <div style="text-align:right;"><div style="font-size:0.7rem;color:#888;font-weight:700;text-transform:uppercase;margin-bottom:2px;">SENSEX</div><div style="font-size:1.1rem;font-weight:700;color:#111;margin-bottom:2px;">73,420</div><div style="font-size:0.8rem;color:#10b981;font-weight:700;">▲ +0.43%</div></div>
        <div style="text-align:right;"><div style="font-size:0.7rem;color:#888;font-weight:700;text-transform:uppercase;margin-bottom:2px;">NIFTY 50</div><div style="font-size:1.1rem;font-weight:700;color:#111;margin-bottom:2px;">22,197</div><div style="font-size:0.8rem;color:#10b981;font-weight:700;">▲ +0.44%</div></div>
        <div style="text-align:right;"><div style="font-size:0.7rem;color:#888;font-weight:700;text-transform:uppercase;margin-bottom:2px;">USD/INR</div><div style="font-size:1.1rem;font-weight:700;color:#111;margin-bottom:2px;">83.74</div><div style="font-size:0.8rem;color:#ef4444;font-weight:700;">▼ -0.12</div></div>
        <div style="width:48px;height:48px;background:#ef4444;color:#fff;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:1.2rem;margin-left:1rem;">RK</div>
    </div>
</div>
""", unsafe_allow_html=True)

page = st.radio(
    "Navigate",
    ["🏠 Home", "📰 My ET — Newsroom", "📖 Story Arc Tracker", "📄 News Summarizer", "🌐 Vernacular Engine"],
    horizontal=True,
    label_visibility="collapsed",
)

# ── Sidebar Settings ────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### Settings & Info")
'''

text = text.replace("color:#FFFFFF", "color:#111111")
text = text.replace("color:#fff;", "color:#111;")
text = text.replace("color: #FFFFFF", "color: #111111")
text = text.replace("color:#e8e0d5", "color:#111")
text = text.replace("color:#ccc", "color:#444")
text = text.replace("color: #ccc", "color: #444")

# Insert the replacement (Wait old_sidebar might have been affected by color replace, let's just do text replace safely)
old_sidebar_mod = old_sidebar
old_sidebar_mod = old_sidebar_mod.replace("color:#FFFFFF", "color:#111111")
text = text.replace(old_sidebar_mod, new_top_level)

# Remove all inner et-headers
text = re.sub(r'st\.markdown\("""\s*<div class="et-header">.*?</div>\s*""", unsafe_allow_html=True\)', '', text, flags=re.DOTALL)

with open('/Users/ajiteshdwivedi/Downloads/ET-Gen-AI-Hackathon-brainiac/streamlit_app.py', 'w') as f:
    f.write(text)
print("File updated successfully.")
