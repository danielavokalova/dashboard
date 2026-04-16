import streamlit as st
import json
from pathlib import Path
from core.ui import apply_theme, gol_header

st.set_page_config(page_title="Průvodci – GOL", page_icon="🗺️", layout="wide")
apply_theme()
gol_header("Průvodci")

st.markdown("### 🗺️ Guided Walkthroughs")
st.caption("Krok po kroku průvodci pro běžné úkoly.")

scenarios_path = Path("data/walkthroughs/scenarios.json")
if scenarios_path.exists():
    scenarios = json.loads(scenarios_path.read_text(encoding="utf-8"))
else:
    scenarios = []
    st.warning("Soubor `data/walkthroughs/scenarios.json` nenalezen.")

if scenarios:
    names = [s["title"] for s in scenarios]
    selected = st.selectbox("Vyber scénář:", names)
    scenario = next(s for s in scenarios if s["title"] == selected)

    st.markdown(f"**{scenario.get('description', '')}**")
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    for i, step in enumerate(scenario.get("steps", []), 1):
        with st.expander(f"Krok {i} — {step['title']}", expanded=(i == 1)):
            st.markdown(step["content"])
