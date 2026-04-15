"""
Page 2 – Guided Walkthroughs (L1 support layer)
Interactive step-by-step guides loaded from data/walkthroughs/scenarios.json.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import json
import streamlit as st

st.set_page_config(
    page_title="Guided Walkthroughs · New Help Portal",
    page_icon="🗺️",
    layout="wide",
)

SCENARIOS_FILE = Path(__file__).parent.parent / "data" / "walkthroughs" / "scenarios.json"


@st.cache_data
def load_scenarios() -> list[dict]:
    if not SCENARIOS_FILE.exists():
        return []
    return json.loads(SCENARIOS_FILE.read_text(encoding="utf-8"))


scenarios = load_scenarios()

st.title("🗺️ Guided Walkthroughs")
st.caption("Follow interactive step-by-step guides for the most common tasks in GOL IBE.")

if not scenarios:
    st.warning("No walkthroughs loaded. Add scenarios to `data/walkthroughs/scenarios.json`.")
    st.stop()

# ── Selector ──────────────────────────────────────────────────────────────────
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

# ── Player ────────────────────────────────────────────────────────────────────
with col2:
    st.markdown(f"#### {scenario['icon']}  {scenario['title']}")
    st.caption(scenario.get("description", ""))

    steps = scenario.get("steps", [])
    total = len(steps)
    state_key = f"step_{selected_title}"

    if state_key not in st.session_state:
        st.session_state[state_key] = 0

    step_idx = st.session_state[state_key]
    step = steps[step_idx]

    st.progress((step_idx + 1) / total, text=f"Step {step_idx + 1} of {total}")

    with st.container(border=True):
        st.markdown(f"**{step['title']}**")
        st.markdown(step["content"])
        if step.get("tip"):
            st.info(f"💡 {step['tip']}")
        if step.get("gif"):
            st.image(step["gif"], use_container_width=True)
        else:
            st.markdown(
                "<div style='background:#f1f5f9;border-radius:8px;height:120px;"
                "display:flex;align-items:center;justify-content:center;"
                "color:#94a3b8;font-size:13px'>🎬 Screenshot / animation goes here</div>",
                unsafe_allow_html=True,
            )

    nav_cols = st.columns([1, 1, 1])
    with nav_cols[0]:
        if st.button("← Back", disabled=step_idx == 0, use_container_width=True):
            st.session_state[state_key] -= 1
            st.rerun()
    with nav_cols[1]:
        st.markdown(
            f"<p style='text-align:center;color:#94a3b8;margin-top:8px'>{step_idx+1} / {total}</p>",
            unsafe_allow_html=True,
        )
    with nav_cols[2]:
        if step_idx < total - 1:
            if st.button("Next →", type="primary", use_container_width=True):
                st.session_state[state_key] += 1
                st.rerun()
        else:
            st.success("✅ Guide complete!")
            if st.button("Restart", use_container_width=True):
                st.session_state[state_key] = 0
                st.rerun()
