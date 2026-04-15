"""
New Help Portal – GOL IBE Admin Console
Main Streamlit entry point.

Run locally:
    cd customer-portal
    streamlit run app.py

Requires:
    pip install -r requirements.txt
    Copy .env.example → .env and fill in ANTHROPIC_API_KEY
"""

import sys
from pathlib import Path

# Ensure project root is on the path so 'core' is importable from all pages
ROOT = Path(__file__).parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st
from core.search import omnisearch_results

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="New Help Portal",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
css_path = ROOT / "assets" / "style.css"
if css_path.exists():
    st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)

# ── Sidebar navigation ────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ✈️ New Help Portal")
    st.caption("GOL IBE Admin Console")
    st.markdown("---")
    st.page_link("app.py",                      label="🏠  Home")
    st.page_link("pages/1_AI_Assistant.py",     label="🤖  AI Assistant")
    st.page_link("pages/2_Walkthroughs.py",     label="🗺️  Guided Walkthroughs")
    st.page_link("pages/3_Agency_Health.py",    label="📊  Agency Health Check")
    st.page_link("pages/4_Changelog.py",        label="🆕  What's New")
    st.markdown("---")
    st.caption("v0.1 · Help Center prototype")

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="hero">
        <h1>✈️ New Help Portal</h1>
        <p>Your smart guide to the GOL IBE Admin Console. Get answers instantly.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Omnisearch ────────────────────────────────────────────────────────────────
query = st.text_input(
    label="omnisearch",
    placeholder="🔍  Search anything… e.g. 'add new user', 'configure markup', 'cancel reservation'",
    label_visibility="collapsed",
    key="omnisearch_input",
)

if query:
    results = omnisearch_results(query)
    if results:
        st.markdown("**Quick results:**")
        for r in results[:5]:
            with st.expander(f"{r['icon']}  {r['title']}  · *{r['category']}*"):
                st.markdown(r["summary"])
                st.page_link("pages/2_Walkthroughs.py", label="Open full guide →")
    else:
        st.info("No results found. Try the 🤖 AI Assistant for a detailed answer.")
    st.divider()

# ── Category cards ────────────────────────────────────────────────────────────
st.markdown("### Browse by topic")

CATEGORIES = [
    ("🏢", "Agency",            "Profile, settings, branding",          "pages/2_Walkthroughs.py"),
    ("🤝", "Dealers",           "Dealer accounts and commissions",       "pages/2_Walkthroughs.py"),
    ("👤", "Customers",         "Passenger profiles and loyalty data",   "pages/2_Walkthroughs.py"),
    ("🎫", "Reservations",      "Create, modify and cancel bookings",    "pages/2_Walkthroughs.py"),
    ("💰", "Prices & Markup",   "Fares, markups and surcharges",         "pages/2_Walkthroughs.py"),
    ("📋", "Code Lists",        "Carriers, destinations, cache",         "pages/2_Walkthroughs.py"),
    ("👥", "Users",             "Agents, roles, passwords",              "pages/2_Walkthroughs.py"),
    ("🔔", "Notifications",     "Email templates and alerts",            "pages/2_Walkthroughs.py"),
    ("📄", "Supporting Texts",  "Terms, conditions, content blocks",     "pages/2_Walkthroughs.py"),
    ("📈", "Statistics",        "Reports and usage analytics",           "pages/3_Agency_Health.py"),
    ("⚙️", "Basic Settings",   "First-time setup and core config",      "pages/2_Walkthroughs.py"),
    ("🔬", "Advanced Settings", "GDS connectors, APIs, webhooks",        "pages/2_Walkthroughs.py"),
]

cols = st.columns(4)
for i, (icon, name, desc, link) in enumerate(CATEGORIES):
    with cols[i % 4]:
        st.markdown(
            f"""<div class="cat-card">
                <div class="cat-icon">{icon}</div>
                <div class="cat-name">{name}</div>
                <div class="cat-desc">{desc}</div>
            </div>""",
            unsafe_allow_html=True,
        )
        st.page_link(link, label="Explore →")
    if (i + 1) % 4 == 0 and i < len(CATEGORIES) - 1:
        cols = st.columns(4)

# ── Popular articles ──────────────────────────────────────────────────────────
st.divider()
st.markdown("### 🔥 Most visited")

POPULAR = [
    ("🔑", "How to reset an agent password",       "Users"),
    ("➕", "Add a new user to your agency",         "Users"),
    ("✈️", "Create your first air reservation",    "Reservations"),
    ("💸", "Set up agency markup rules",            "Prices & Markup"),
    ("📧", "Customise booking confirmation email",  "Notifications"),
    ("🔌", "Connect a GDS / NDC source",            "Advanced Settings"),
]

for icon, title, cat in POPULAR:
    c1, c2 = st.columns([8, 2])
    with c1:
        st.markdown(
            f"{icon} **{title}** &nbsp;<span class='badge'>{cat}</span>",
            unsafe_allow_html=True,
        )
    with c2:
        st.page_link("pages/2_Walkthroughs.py", label="Open →")
