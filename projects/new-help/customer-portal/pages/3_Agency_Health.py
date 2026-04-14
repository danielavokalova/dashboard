import streamlit as st

st.set_page_config(page_title="Agency Health", page_icon="📊", layout="wide")
st.title("📊 Agency Health Check")
st.caption("Vizuální přehled toho, jak efektivně klient systém využívá.")

st.info("Tato sekce bude napojena na data z Google Sheets / Metabase.")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Tickets tento měsíc", "—", help="Počet rezervací")
with col2:
    st.metric("Aktivní uživatelé", "—", help="Počet přihlášení za 30 dní")
with col3:
    st.metric("Využití notifikací", "—", help="% zapnutých notifikací")
