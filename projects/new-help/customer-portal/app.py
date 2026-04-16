import streamlit as st
from pathlib import Path

st.set_page_config(
    page_title="New Help Portal",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ─────────────────────────────────────────────────────────
_CSS = Path(__file__).parent / "assets" / "style.css"
st.markdown(f"<style>{_CSS.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

# ── Sidebar branding ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <span style="font-size:1.3rem;">✈️</span>
        <div>
            <div class="sidebar-title">New Help Portal</div>
            <div class="sidebar-sub">GOL IBE Admin Console</div>
        </div>
    </div>
    <hr class="sidebar-hr">
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="sidebar-version">v0.1 · Help Center prototype</div>
    """, unsafe_allow_html=True)

# ── Hero banner ──────────────────────────────────────────────────
st.markdown("""
<div class="hero-banner">
    <div class="hero-title">✈️ New Help Portal</div>
    <div class="hero-sub">Your smart guide to the GOL IBE Admin Console. Get answers instantly.</div>
</div>
""", unsafe_allow_html=True)

# ── Search ───────────────────────────────────────────────────────
query = st.text_input(
    "",
    placeholder="🔍  Search anything… e.g. 'add new user', 'configure markup', 'cancel reservation'",
    label_visibility="collapsed",
)
if query and query.strip():
    from core.search import search
    hits = search(query)
    if hits:
        for h in hits:
            st.markdown(f"**{h['title']}** — {h['snippet']}")
    else:
        st.info("Žádné výsledky. Zkus jiný dotaz nebo použij AI Assistanta.")

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
st.markdown("### Browse by topic")
st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

# ── Topic tiles ──────────────────────────────────────────────────
topics = [
    ("🏢", "Agency",          "Profile, settings, branding"),
    ("🤝", "Dealers",         "Dealer accounts and commissions"),
    ("👤", "Customers",       "Passenger profiles and loyalty data"),
    ("🎫", "Reservations",    "Create, modify and cancel bookings"),
    ("💰", "Prices & Markup", "Fares, markups and surcharges"),
    ("📋", "Code Lists",      "Carriers, destinations, cache"),
    ("👥", "Users",           "Agents, roles, passwords"),
    ("🔔", "Notifications",   "Email templates and alerts"),
]

def _card(icon, title, sub):
    return f"""
    <div class="topic-card">
      <div class="topic-icon">{icon}</div>
      <div class="topic-title">{title}</div>
      <div class="topic-sub">{sub}</div>
    </div>
    """

row1 = st.columns(4, gap="medium")
row2 = st.columns(4, gap="medium")

for col, (icon, title, sub) in zip(row1, topics[:4]):
    with col:
        st.markdown(_card(icon, title, sub), unsafe_allow_html=True)
        st.markdown("<div class='explore-link'>Explore →</div>", unsafe_allow_html=True)

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

for col, (icon, title, sub) in zip(row2, topics[4:]):
    with col:
        st.markdown(_card(icon, title, sub), unsafe_allow_html=True)
        st.markdown("<div class='explore-link'>Explore →</div>", unsafe_allow_html=True)
