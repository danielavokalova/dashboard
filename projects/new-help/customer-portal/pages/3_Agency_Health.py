import streamlit as st
from core.ui import apply_theme, gol_header

st.set_page_config(page_title="Agency Health – GOL", page_icon="📊", layout="wide")
apply_theme()
gol_header("Agency Health")

st.markdown("### 📊 Agency Health Check")
st.caption("Vizuální přehled toho, jak efektivně klient systém využívá.")

st.info("Tato sekce bude napojena na data z Google Sheets / Metabase.")

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3, gap="medium")
with col1:
    st.metric("Tickets tento měsíc", "—", help="Počet rezervací")
with col2:
    st.metric("Aktivní uživatelé", "—", help="Počet přihlášení za 30 dní")
with col3:
    st.metric("Využití notifikací", "—", help="% zapnutých notifikací")
