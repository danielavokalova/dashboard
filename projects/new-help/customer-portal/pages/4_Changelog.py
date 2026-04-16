import streamlit as st
import json
from pathlib import Path
from core.ui import apply_theme, gol_header

st.set_page_config(page_title="Changelog – GOL", page_icon="🆕", layout="wide")
apply_theme()
gol_header("Co je nového")

st.markdown("### 🆕 Visual Changelog")
st.caption("Interaktivní přehled novinek s ukázkami.")

entries_path = Path("data/changelog/entries.json")
if entries_path.exists():
    entries = json.loads(entries_path.read_text(encoding="utf-8"))
else:
    entries = []
    st.warning("Soubor `data/changelog/entries.json` nenalezen.")

for entry in entries:
    st.markdown(f"""
    <div style="
        background:#ffffff; border-radius:14px;
        border:1.5px solid #e2eaf2;
        box-shadow:0 2px 10px rgba(26,39,68,0.06);
        padding:24px 28px; margin-bottom:16px;
    ">
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:8px;">
            <span style="
                background:#F26322; color:#fff; border-radius:20px;
                padding:3px 14px; font-size:0.85rem; font-weight:800;
            ">{entry['version']}</span>
            <span style="color:#6b7a99;font-size:0.88rem;font-weight:600;">{entry['date']}</span>
        </div>
        <div style="color:#1a2744;font-weight:700;font-size:1rem;margin-bottom:8px;">{entry.get('summary','')}</div>
    </div>
    """, unsafe_allow_html=True)

    if entry.get("gif"):
        st.image(entry["gif"], caption=entry.get("gif_caption", ""))

    for item in entry.get("items", []):
        st.markdown(f"✦ {item}")

    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
