import streamlit as st
import json
from pathlib import Path

st.set_page_config(page_title="Co je nového", page_icon="📢", layout="wide")
st.title("📢 Visual Changelog")
st.caption("Interaktivní přehled novinek s ukázkami.")

entries_path = Path("data/changelog/entries.json")
if entries_path.exists():
    entries = json.loads(entries_path.read_text(encoding="utf-8"))
else:
    entries = []
    st.warning("Soubor `data/changelog/entries.json` nenalezen.")

for entry in entries:
    with st.container(border=True):
        st.markdown(f"### {entry['version']} — {entry['date']}")
        st.markdown(entry.get("summary", ""))
        if entry.get("gif"):
            st.image(entry["gif"], caption=entry.get("gif_caption", ""))
        for item in entry.get("items", []):
            st.markdown(f"- {item}")
