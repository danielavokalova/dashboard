"""
Page 4 – What's New (Visual Changelog)
────────────────────────────────────────
Interactive release notes with visual previews (GIFs / screenshots).
Entries are loaded from data/changelog/entries.json.
"""

import json
from pathlib import Path
import streamlit as st

st.set_page_config(
    page_title="What's New · GOL IBE Help",
    page_icon="🆕",
    layout="wide",
)

CHANGELOG_FILE = Path(__file__).parent.parent / "data" / "changelog" / "entries.json"


@st.cache_data
def load_changelog() -> list[dict]:
    if not CHANGELOG_FILE.exists():
        return []
    return json.loads(CHANGELOG_FILE.read_text(encoding="utf-8"))


entries = load_changelog()

st.title("🆕 What's New in GOL IBE")
st.caption("Stay up to date with the latest features, improvements and fixes.")

if not entries:
    st.info("No changelog entries yet. Add releases to `data/changelog/entries.json`.")
    st.stop()

# Group by version
for entry in entries:
    with st.container(border=True):
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"### {entry.get('emoji', '🆕')}  {entry['title']}")
            st.caption(f"Version {entry['version']}  ·  {entry['date']}")
        with col2:
            badge_color = {"feature": "🟢", "improvement": "🔵", "fix": "🟡"}.get(
                entry.get("type", "feature"), "⚪"
            )
            st.markdown(
                f"<span style='font-size:13px'>{badge_color} {entry.get('type','feature').title()}</span>",
                unsafe_allow_html=True,
            )

        st.markdown(entry["description"])

        if entry.get("gif"):
            st.image(entry["gif"], use_container_width=True)
        elif entry.get("highlights"):
            for h in entry["highlights"]:
                st.markdown(f"- {h}")

        if entry.get("guide_link"):
            st.page_link("pages/2_Walkthroughs.py", label="📖 See how to use this →")

        st.markdown("")
