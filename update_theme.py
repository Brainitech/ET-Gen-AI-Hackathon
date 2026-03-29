import re

with open('/Users/ajiteshdwivedi/Downloads/ET-Gen-AI-Hackathon-brainiac/streamlit_app.py', 'r') as f:
    text = f.read()

# Replace the static CSS with dynamic CSS variables based on toggle

sidebar_css_replacement = """
col_spacer, col_toggle = st.columns([9, 1])
with col_toggle:
    dark_mode = st.toggle("🌙 Dark", value=False)

if dark_mode:
    theme_vars = '''
    :root {
        --bg-col: #0d0d0d;
        --text-col: #e8e0d5;
        --card-bg: #1a1a1a;
        --border-col: #2a2a2a;
        --sub-text: #888;
        --input-bg: #1a1a1a;
        --highlight: #B22222;
        --brand-red: #B22222;
    }
    '''
else:
    theme_vars = '''
    :root {
        --bg-col: #fdfdfd;
        --text-col: #111;
        --card-bg: #fff;
        --border-col: #e5e7eb;
        --sub-text: #555;
        --input-bg: #fff;
        --highlight: #fef2f2;
        --brand-red: #ef4444;
    }
    '''

st.markdown(f'''
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;800&family=Inter:wght@400;500;600;700&display=swap');
{theme_vars}
html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}
.stApp {{ background: var(--bg-col); color: var(--text-col); }}
header[data-testid="stHeader"] {{ display: none; }}
.top-ticker {{ background: #111; color: #fff; padding: 0.35rem 2rem; font-size: 0.75rem; display: flex; align-items: center; font-weight: 500; margin: -1rem -4rem 1rem -4rem; }}
.et-header-light {{ padding: 1rem 0; display: flex; align-items: center; justify-content: space-between; border-bottom: 2px solid var(--brand-red); margin-bottom: 1.5rem; }}
.et-logo-light {{ font-family: 'Playfair Display', serif; font-size: 3.5rem; font-weight: 800; color: var(--brand-red); line-height: 1; margin-bottom: -4px; }}
.et-tagline-light {{ color: var(--sub-text); font-size: 0.7rem; font-weight: 700; letter-spacing: 0.15em; text-transform: uppercase; margin-top: 4px; }}
.hero-banner {{ background: var(--card-bg); border: 1px solid var(--border-col); border-left: 5px solid var(--brand-red); border-radius: 8px; padding: 2rem; margin-bottom: 2rem; }}
.hero-title {{ font-family: 'Playfair Display', serif; font-size: 2.2rem; font-weight: 800; color: var(--text-col); margin: 0; }}
.hero-sub {{ color: var(--sub-text); font-size: 1rem; margin-top: 0.6rem; }}
.glass-card {{ background: var(--card-bg); border: 1px solid var(--border-col); border-radius: 8px; padding: 1.5rem; margin-bottom: 1rem; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }}
.section-heading {{ display: flex; align-items: center; gap: 0.6rem; font-size: 0.8rem; font-weight: 700; color: var(--text-col); text-transform: uppercase; margin: 1.5rem 0 1rem; padding: 0.5rem 1rem; background: var(--card-bg); border-left: 3px solid var(--brand-red); border-radius: 0 4px 4px 0; }}
.section-label {{ font-size: 0.75rem; font-weight: 700; color: var(--text-col); text-transform: uppercase; margin-bottom: 1rem; padding-bottom: 0.5rem; border-bottom: 1px solid var(--border-col); }}
.news-card {{ background: var(--card-bg); border: 1px solid var(--border-col); border-top: 4px solid var(--brand-red); border-radius: 8px; padding: 1.5rem; margin-bottom: 1rem; box-shadow: 0 2px 8px rgba(0,0,0,0.04); }}
.news-meta {{ display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.5rem; }}
.news-source {{ font-size: 0.7rem; font-weight: 700; color: var(--brand-red); text-transform: uppercase; }}
.news-time {{ color: var(--sub-text); font-size: 0.7rem; }}
.news-title {{ font-size: 1.4rem; font-family: 'Playfair Display', serif; font-weight: 800; color: var(--text-col); line-height: 1.3; margin-bottom: 0.5rem; }}
.news-summary {{ color: var(--text-col); font-size: 0.95rem; line-height: 1.6; margin-bottom: 0.75rem; opacity:0.8; }}
div[data-testid="stRadio"] > div {{ flex-direction: row; gap: 2rem; border-bottom: 2px solid var(--border-col); padding-bottom: 0; margin-bottom: 1rem; }}
div[data-testid="stRadio"] label {{ padding: 0.8rem 0; cursor: pointer !important; margin: 0; }}
div[data-testid="stRadio"] label > div:first-child {{ display: none; }}
div[data-testid="stRadio"] label > div:last-child {{ font-weight: 700 !important; font-size: 0.85rem !important; color: var(--sub-text) !important; text-transform: uppercase !important; }}
div[data-testid="stRadio"] label[data-checked="true"] {{ border-bottom: 3px solid var(--brand-red); }}
div[data-testid="stRadio"] label[data-checked="true"] > div:last-child {{ color: var(--brand-red) !important; }}
.stMetric {{ background: var(--card-bg); border: 1px solid var(--border-col); border-top: 2px solid var(--text-col); border-radius: 6px; padding: 1rem; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }}
.persona-card {{ background: var(--card-bg); border: 2px solid var(--border-col); border-radius: 12px; padding: 1.5rem; text-align: center; cursor: pointer; }}
.persona-card.selected {{ border-color: var(--brand-red); background: var(--highlight); }}
.persona-name {{ font-weight: 700; font-size: 1rem; color: var(--text-col); margin-bottom: 0.25rem; }}
.persona-desc {{ color: var(--sub-text); font-size: 0.8rem; line-height: 1.5; }}
.ai-snippet {{ background: var(--card-bg); border: 1px solid var(--border-col); border-left: 3px solid #d97706; border-radius: 6px; padding: 0.85rem 1rem; margin-top: 0.85rem; }}
.ai-snippet-label {{ font-size: 0.65rem; font-weight: 700; color: #d97706; text-transform: uppercase; margin-bottom: 0.35rem; }}
.ai-snippet-text {{ color: var(--text-col); font-size: 0.9rem; line-height: 1.6; font-style: italic; opacity:0.9; }}
.stButton>button {{ background: var(--card-bg) !important; color: var(--text-col) !important; border: 1px solid var(--border-col) !important; border-radius: 6px !important; font-weight: 600 !important; }}
.stButton>button:hover {{ border-color: #9ca3af !important; }}
.deep-dive-section {{ background: var(--card-bg); border: 1px solid var(--border-col); border-left: 3px solid var(--brand-red); border-radius: 6px; padding: 1rem; margin-bottom: 0.75rem; color: var(--text-col); }}
.deep-dive-heading {{ font-weight: 700; color: var(--brand-red); margin-bottom: 0.4rem; font-size:0.85rem; }}
.deep-dive-content {{ color: var(--text-col); font-size:0.9rem; }}
.bottom-line {{ background: rgba(24cd,211,77,0.1); border: 1px solid rgba(252,211,77,0.5); border-radius: 6px; padding: 1rem; color:#92400e; margin-top:1rem; }}
.bottom-line-label {{ font-size:0.75rem; font-weight:700; color:#b45309; text-transform:uppercase; margin-bottom:0.3rem;}}
.gloss-card {{ background:var(--card-bg); border:1px solid var(--border-col); border-left:3px solid #8b5cf6; border-radius:6px; padding:0.75rem; color:var(--text-col); }}
.gloss-term {{ font-weight:700; color:#7c3aed; font-size:0.9rem; }}
.err-box {{ background: rgba(239,68,68,0.1); border: 1px solid rgba(239,68,68,0.2); border-radius: 6px; padding: 1rem; color: #ef4444; }}
.info-box {{ background: var(--card-bg); border: 1px solid var(--border-col); border-radius: 6px; padding: 1rem; color: var(--text-col); }}
.tag {{ background: rgba(128,128,128,0.1); border: 1px solid var(--border-col); color: var(--text-col); font-size: 0.7rem; font-weight: 600; padding: 0.2rem 0.6rem; border-radius: 999px; }}
.dot-positive {{ color: #10b981; }} .dot-negative {{ color: #ef4444; }} .dot-neutral {{ color: #94a3b8; }}
.badge-positive {{ background: rgba(21,128,61,0.1); color: #10b981; border: 1px solid rgba(21,128,61,0.2); padding:2px 8px; border-radius:12px; font-size:0.75rem;}}
.badge-negative {{ background: rgba(185,28,28,0.1); color: #ef4444; border: 1px solid rgba(185,28,28,0.2); padding:2px 8px; border-radius:12px; font-size:0.75rem;}}
.timeline-dot {{ width:10px; height:10px; border-radius:50%; background:var(--brand-red); margin-top:5px; box-shadow:0 0 0 3px rgba(239,68,68,0.2); }}
.player-card {{ background:var(--card-bg); border:1px solid var(--border-col); border-left: 3px solid var(--brand-red); padding:1rem; border-radius:6px; margin-bottom:0.5rem;}}
.stTextInput input, .stTextArea textarea, .stSelectbox select {{ background:var(--input-bg)!important; color:var(--text-col)!important; border-color:var(--border-col)!important; }}
</style>
''', unsafe_allow_html=True)
"""

# Replace old CSS logic
text = re.sub(r'st\.markdown\("""\n<style>.*?</style>\n""", unsafe_allow_html=True\)', sidebar_css_replacement, text, flags=re.DOTALL)

# Inline stylings were previously replaced with #111111 and #111. Let's make them var(--text-col)
text = text.replace("color:#111111", "color: var(--text-col)")
text = text.replace("color: #111111", "color: var(--text-col)")
text = text.replace("color:#111", "color: var(--text-col)")
text = text.replace("color:#000", "color: var(--text-col)")
text = text.replace("color:#444", "color: var(--text-col)")
text = text.replace("color:#666", "color: var(--sub-text)")

# Look for the header and remove the market numbers and RK avatar
old_header = '''<div class="et-header-light">
    <div>
        <div class="et-logo-light">ET</div>
        <div class="et-tagline-light">ECONOMIC TIMES INTELLIGENCE</div>
        <div style="margin-top:8px;"><span style="background:var(--text-col); color:var(--text-col); font-size:0.75rem; font-weight:600; padding:4px 8px; border-radius:4px;">● AI-Powered Newsroom · Live</span></div>
    </div>
    <div style="display:flex; gap:2.5rem; align-items:center;">
        <div style="text-align:right;"><div style="font-size:0.7rem;color:var(--sub-text);font-weight:700;text-transform:uppercase;margin-bottom:2px;">SENSEX</div><div style="font-size:1.1rem;font-weight:700;color:var(--text-col);margin-bottom:2px;">73,420</div><div style="font-size:0.8rem;color:#10b981;font-weight:700;">▲ +0.43%</div></div>
        <div style="text-align:right;"><div style="font-size:0.7rem;color:var(--sub-text);font-weight:700;text-transform:uppercase;margin-bottom:2px;">NIFTY 50</div><div style="font-size:1.1rem;font-weight:700;color:var(--text-col);margin-bottom:2px;">22,197</div><div style="font-size:0.8rem;color:#10b981;font-weight:700;">▲ +0.44%</div></div>
        <div style="text-align:right;"><div style="font-size:0.7rem;color:var(--sub-text);font-weight:700;text-transform:uppercase;margin-bottom:2px;">USD/INR</div><div style="font-size:1.1rem;font-weight:700;color:var(--text-col);margin-bottom:2px;">83.74</div><div style="font-size:0.8rem;color:#ef4444;font-weight:700;">▼ -0.12</div></div>
        <div style="width:48px;height:48px;background:#ef4444;color:var(--text-col);border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:1.2rem;margin-left:1rem;">RK</div>
    </div>
</div>'''

# Wait, the color replaces I did might have affected the header content (e.g., color:#111 replaced with color:var(--text-col) and color:#fff replaced earlier to something else?)
# Let's just use regex to replace everything after `<div class="et-logo-light">` to the end of `</div>`
replacement_header = '''<div class="et-header-light">
    <div>
        <div class="et-logo-light">ET</div>
        <div class="et-tagline-light">ECONOMIC TIMES INTELLIGENCE</div>
        <div style="margin-top:8px;"><span style="background:var(--brand-red); color:#fff; font-size:0.65rem; font-weight:700; padding:2px 8px; border-radius:99px;">● LIVE</span></div>
    </div>
</div>'''

text = re.sub(r'<div class="et-header-light">.*?</div>\n</div>', replacement_header, text, flags=re.DOTALL)

with open('/Users/ajiteshdwivedi/Downloads/ET-Gen-AI-Hackathon-brainiac/streamlit_app.py', 'w') as f:
    f.write(text)

print("Theme installed.")
