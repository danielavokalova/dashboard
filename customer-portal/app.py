"""
GOL IBE Customer Portal – Smart Hub 360
Main Streamlit entry point.

Run locally:
    streamlit run app.py

Requires:
    pip install -r requirements.txt
    Copy .env.example → .env and fill in ANTHROPIC_API_KEY
"""

import streamlit as st
from core.search import omnisearch_results

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="GOL IBE Help Center",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS (branding + Cmd+K search overlay) ──────────────────────────────
with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ── Sidebar navigation ────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://via.placeholder.com/160x40?text=GOL+IBE", width=160)
    st.markdown("---")
    st.markdown("### Navigation")
    st.page_link("app.py",                       label="🏠  Home",              )
    st.page_link("pages/1_AI_Assistant.py",      label="🤖  AI Assistant",      )
    st.page_link("pages/2_Walkthroughs.py",      label="🗺️  Guided Walkthroughs",)
    st.page_link("pages/3_Agency_Health.py",     label="📊  Agency Health Check",)
    st.page_link("pages/4_Changelog.py",         label="🆕  What's New",         )
    st.markdown("---")
    st.caption("GOL IBE Admin Console · Help Center v0.1")

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="hero">
        <h1>✈️ GOL IBE Help Center</h1>
        <p>Your smart guide to the Admin Console. Get answers instantly.</p>
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
                st.page_link(r["page_link"], label="Open full guide →")
    else:
        st.info("No results found. Try the AI Assistant for a detailed answer.")
    st.divider()

# ── Category cards ────────────────────────────────────────────────────────────
st.markdown("### Browse by topic")

CATEGORIES = [
    ("🏢", "Agency",            "Agency profile, settings, branding",       "pages/2_Walkthroughs.py"),
    ("🤝", "Dealers",           "Dealer accounts and commissions",           "pages/2_Walkthroughs.py"),
    ("👤", "Customers",         "Passenger profiles and loyalty data",       "pages/2_Walkthroughs.py"),
    ("🎫", "Reservations",      "Create, modify and cancel bookings",        "pages/2_Walkthroughs.py"),
    ("💰", "Prices & Markup",   "Fares, markups and surcharges",             "pages/2_Walkthroughs.py"),
    ("📋", "Code Lists",        "Airport codes, carriers, currencies",       "pages/2_Walkthroughs.py"),
    ("👥", "Users",             "Manage agent accounts and permissions",     "pages/2_Walkthroughs.py"),
    ("🔔", "Notifications",     "Email templates and alert rules",           "pages/2_Walkthroughs.py"),
    ("📄", "Supporting Texts",  "Terms, conditions and custom copy",         "pages/2_Walkthroughs.py"),
    ("📈", "Statistics",        "Reports and usage analytics",               "pages/3_Agency_Health.py"),
    ("⚙️", "Basic Settings",   "First-time setup and core config",          "pages/2_Walkthroughs.py"),
    ("🔬", "Advanced Settings", "GDS connectors, APIs, webhooks",            "pages/2_Walkthroughs.py"),
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
        st.page_link(link, label=f"Explore →")
    if (i + 1) % 4 == 0 and i < len(CATEGORIES) - 1:
        cols = st.columns(4)

# ── Quick wins (popular articles) ─────────────────────────────────────────────
st.divider()
st.markdown("### 🔥 Most visited")

POPULAR = [
    ("🔑", "How to reset an agent password",         "Users"),
    ("➕", "Add a new user to your agency",           "Users"),
    ("✈️", "Create your first air reservation",      "Reservations"),
    ("💸", "Set up agency markup rules",              "Prices & Markup"),
    ("📧", "Customise booking confirmation email",    "Notifications"),
    ("🔌", "Connect a GDS / NDC source",              "Advanced Settings"),
]

for icon, title, cat in POPULAR:
    c1, c2 = st.columns([8, 2])
    with c1:
        st.markdown(f"{icon} **{title}**  <span class='badge'>{cat}</span>", unsafe_allow_html=True)
    with c2:
        st.page_link("pages/2_Walkthroughs.py", label="Open →")
