import streamlit as st
import json
from pathlib import Path

st.set_page_config(page_title="Guided Walkthroughs – New Help Portal", page_icon="📘", layout="wide")

_CSS = Path(__file__).parent.parent / "assets" / "style.css"
st.markdown(f"<style>{_CSS.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

st.markdown("### 📘 Guided Walkthroughs")
st.caption("Step-by-step guides for common tasks.")

scenarios_path = Path(__file__).parent.parent / "data" / "walkthroughs" / "scenarios.json"
if scenarios_path.exists():
    scenarios = json.loads(scenarios_path.read_text(encoding="utf-8"))
else:
    scenarios = []
    st.warning("scenarios.json not found.")

if scenarios:
    names = [s["title"] for s in scenarios]
    selected = st.selectbox("Select scenario:", names)
    scenario = next(s for s in scenarios if s["title"] == selected)

    st.markdown(f"**{scenario.get('description', '')}**")
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    for i, step in enumerate(scenario.get("steps", []), 1):
        with st.expander(f"Step {i} — {step['title']}", expanded=(i == 1)):
            st.markdown(step["content"])
