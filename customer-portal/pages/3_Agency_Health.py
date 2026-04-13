"""
Page 3 – Agency Health Check
─────────────────────────────
Visual dashboard showing how effectively the agency uses the GOL IBE system.
Highlights unused features, configuration gaps, and usage trends.

Data sources (configure in .env):
  - CSV/Excel export from Metabase (current default – drop file in data/)
  - Direct Metabase embed (set METABASE_EMBED_TOKEN)
  - Google Sheets via service account (set GOOGLE_SHEETS_CREDS)
"""

from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Agency Health Check · GOL IBE Help",
    page_icon="📊",
    layout="wide",
)

st.title("📊 Agency Health Check")
st.caption(
    "See how your agency is using GOL IBE and discover features you haven't tried yet."
)

# ── Demo / placeholder data ───────────────────────────────────────────────────
# TODO: replace with real data pull from Metabase / Google Sheets
DEMO_METRICS = {
    "Reservations this month": 142,
    "Tickets issued":          118,
    "Active agents":             7,
    "Open support tickets":      2,
}

FEATURE_USAGE = pd.DataFrame({
    "Feature":    ["Online booking", "Markup rules", "Email notifications",
                   "Customer profiles", "Statistics", "API connector"],
    "Used":       [True, True, True, False, False, False],
    "Setup score":[95, 70, 60, 0, 0, 0],
})

MONTHLY_BOOKINGS = pd.DataFrame({
    "Month":        ["Oct", "Nov", "Dec", "Jan", "Feb", "Mar"],
    "Reservations": [88, 102, 134, 97, 119, 142],
    "Issued":       [72, 90, 122, 80, 99, 118],
})

# ── KPI row ───────────────────────────────────────────────────────────────────
cols = st.columns(len(DEMO_METRICS))
for col, (label, value) in zip(cols, DEMO_METRICS.items()):
    col.metric(label, value)

st.divider()

# ── Charts ────────────────────────────────────────────────────────────────────
c1, c2 = st.columns(2)

with c1:
    st.markdown("#### Monthly activity")
    fig = px.bar(
        MONTHLY_BOOKINGS, x="Month",
        y=["Reservations", "Issued"],
        barmode="group",
        color_discrete_map={"Reservations": "#1e40af", "Issued": "#0ea5e9"},
    )
    fig.update_layout(margin=dict(t=10, b=10), legend_title="")
    st.plotly_chart(fig, use_container_width=True)

with c2:
    st.markdown("#### Feature adoption")
    fig2 = go.Figure(go.Bar(
        x=FEATURE_USAGE["Setup score"],
        y=FEATURE_USAGE["Feature"],
        orientation="h",
        marker_color=["#22c55e" if u else "#e2e8f0" for u in FEATURE_USAGE["Used"]],
        text=[f"{s}%" for s in FEATURE_USAGE["Setup score"]],
        textposition="inside",
    ))
    fig2.update_layout(xaxis_range=[0, 100], margin=dict(t=10, b=10))
    st.plotly_chart(fig2, use_container_width=True)

# ── Recommendations ───────────────────────────────────────────────────────────
st.markdown("#### 💡 Recommendations")
unused = FEATURE_USAGE[~FEATURE_USAGE["Used"]]
for _, row in unused.iterrows():
    with st.expander(f"🔓 Unlock **{row['Feature']}** – not configured yet"):
        st.markdown(
            f"Your agency hasn't set up **{row['Feature']}** yet. "
            "This feature can save you time and improve the booking experience."
        )
        st.page_link("pages/2_Walkthroughs.py", label="👉 Open setup guide")

# ── Data source notice ────────────────────────────────────────────────────────
st.divider()
st.caption(
    "📌 **Demo data only.** Connect real data by setting `METABASE_EMBED_TOKEN` "
    "or `GOOGLE_SHEETS_CREDS` in your `.env` file."
)
