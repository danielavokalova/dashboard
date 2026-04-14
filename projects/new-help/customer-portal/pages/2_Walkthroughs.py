import streamlit as st
import json
from pathlib import Path

st.set_page_config(page_title="Průvodci", page_icon="🗺️", layout="wide")
st.title("🗺️ Guided Walkthroughs")
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

    st.markdown(f"### {scenario['title']}")
    st.caption(scenario.get("description", ""))

    for i, step in enumerate(scenario.get("steps", []), 1):
        with st.expander(f"Krok {i}: {step['title']}", expanded=(i == 1)):
            st.markdown(step["content"])
