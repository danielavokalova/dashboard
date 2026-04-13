"""
Page 2 – Guided Walkthroughs
─────────────────────────────
Interactive step-by-step guides for common tasks in the GOL IBE Admin Console.
Scenarios are loaded from data/walkthroughs/scenarios.json.

L1 support layer: interactive, visual, click-through guides.
"""

import json
from pathlib import Path

import streamlit as st

st.set_page_config(
    page_title="Guided Walkthroughs · GOL IBE Help",
    page_icon="🗺️",
    layout="wide",
)

SCENARIOS_FILE = Path(__file__).parent.parent / "data" / "walkthroughs" / "scenarios.json"

# ── Load scenarios ────────────────────────────────────────────────────────────
@st.cache_data
def load_scenarios() -> list[dict]:
    if not SCENARIOS_FILE.exists():
        return []
    return json.loads(SCENARIOS_FILE.read_text(encoding="utf-8"))


scenarios = load_scenarios()

# ── Header ────────────────────────────────────────────────────────────────────
st.title("🗺️ Guided Walkthroughs")
st.caption("Follow interactive step-by-step guides for the most common tasks.")

if not scenarios:
    st.warning("No walkthroughs loaded yet. Add scenarios to `data/walkthroughs/scenarios.json`.")
    st.stop()

# ── Scenario selector ─────────────────────────────────────────────────────────
categories = sorted({s["category"] for s in scenarios})
selected_cat = st.selectbox("Filter by topic", ["All"] + categories)

filtered = scenarios if selected_cat == "All" else [
    s for s in scenarios if s["category"] == selected_cat
]

col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("#### Choose a guide")
    selected_title = st.radio(
        label="guide",
        options=[s["title"] for s in filtered],
        label_visibility="collapsed",
    )

scenario = next(s for s in filtered if s["title"] == selected_title)

# ── Walkthrough player ────────────────────────────────────────────────────────
with col2:
    st.markdown(f"#### {scenario['icon']}  {scenario['title']}")
    st.caption(scenario.get("description", ""))

    steps = scenario.get("steps", [])
    total = len(steps)

    if f"step_{selected_title}" not in st.session_state:
        st.session_state[f"step_{selected_title}"] = 0

    step_idx = st.session_state[f"step_{selected_title}"]
    step = steps[step_idx]

    # Progress bar
    st.progress((step_idx + 1) / total, text=f"Step {step_idx + 1} of {total}")

    # Step content
    with st.container(border=True):
        st.markdown(f"**{step['title']}**")
        st.markdown(step["content"])

        if step.get("tip"):
            st.info(f"💡 {step['tip']}")

        # GIF/image placeholder
        if step.get("gif"):
            st.image(step["gif"], caption="", use_container_width=True)
        else:
            st.markdown(
                "<div style='background:#f1f5f9;border-radius:8px;height:140px;"
                "display:flex;align-items:center;justify-content:center;"
                "color:#94a3b8;font-size:13px'>🎬 Animation / screenshot goes here</div>",
                unsafe_allow_html=True,
            )

    # Navigation
    nav_cols = st.columns([1, 1, 1])
    with nav_cols[0]:
        if st.button("← Back", disabled=step_idx == 0, use_container_width=True):
            st.session_state[f"step_{selected_title}"] -= 1
            st.rerun()
    with nav_cols[1]:
        st.markdown(f"<p style='text-align:center;color:#94a3b8'>{step_idx+1} / {total}</p>",
                    unsafe_allow_html=True)
    with nav_cols[2]:
        if step_idx < total - 1:
            if st.button("Next →", type="primary", use_container_width=True):
                st.session_state[f"step_{selected_title}"] += 1
                st.rerun()
        else:
            st.success("✅ Guide complete!")
            if st.button("Restart", use_container_width=True):
                st.session_state[f"step_{selected_title}"] = 0
                st.rerun()
