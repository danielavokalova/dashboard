import streamlit as st
from pathlib import Path

st.set_page_config(page_title="Agency Health Check – New Help Portal", page_icon="📊", layout="wide")

_CSS = Path(__file__).parent.parent / "assets" / "style.css"
st.markdown(f"<style>{_CSS.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

st.markdown("### 📊 Agency Health Check")
st.caption("Visual overview of how effectively the agency uses the system.")

st.info("This section will be connected to data from Google Sheets / Metabase.")

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3, gap="medium")
with col1:
    st.metric("Tickets this month", "—", help="Number of reservations")
with col2:
    st.metric("Active users", "—", help="Logins in the last 30 days")
with col3:
    st.metric("Notification usage", "—", help="% with notifications enabled")
