import streamlit as st

st.set_page_config(
    page_title="Customer Portal",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("✈️ Customer Portal")
st.caption("Travelport — interaktivní pomocník pro klienty")

st.markdown("---")

# Omnisearch (Cmd+K placeholder)
query = st.text_input("🔍 Omnisearch — hledej akce, návody, nastavení...", placeholder="Např. 'jak přidat uživatele' nebo 'markup pravidla'")

if query:
    st.info(f"Hledám: **{query}** — Omnisearch bude implementován v `core/search.py`")

st.markdown("---")
st.subheader("Navigace")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.page_link("pages/1_AI_Assistant.py", label="🤖 AI Pomocník", icon="💬")
with col2:
    st.page_link("pages/2_Walkthroughs.py", label="📋 Průvodci", icon="🗺️")
with col3:
    st.page_link("pages/3_Agency_Health.py", label="📊 Agency Health", icon="📈")
with col4:
    st.page_link("pages/4_Changelog.py", label="🆕 Co je nového", icon="📢")
