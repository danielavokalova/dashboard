import streamlit as st
import json
from pathlib import Path

st.set_page_config(page_title="What's New – New Help Portal", page_icon="🆕", layout="wide")

_CSS = Path(__file__).parent.parent / "assets" / "style.css"
st.markdown(f"<style>{_CSS.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

st.markdown("### 🆕 What's New")
st.caption("Interactive release notes with previews.")

entries_path = Path(__file__).parent.parent / "data" / "changelog" / "entries.json"
if entries_path.exists():
    entries = json.loads(entries_path.read_text(encoding="utf-8"))
else:
    entries = []
    st.warning("entries.json not found.")

for entry in entries:
    st.markdown(f"""
    <div class="changelog-card">
        <span class="version-badge">{entry['version']}</span>
        <span style="color:#64748b;font-size:0.86rem;font-weight:600;">{entry['date']}</span>
        <div style="color:#1e293b;font-weight:700;margin-top:10px;margin-bottom:8px;">{entry.get('summary','')}</div>
    </div>
    """, unsafe_allow_html=True)

    if entry.get("gif"):
        st.image(entry["gif"])

    for item in entry.get("items", []):
        st.markdown(f"- {item}")

    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
