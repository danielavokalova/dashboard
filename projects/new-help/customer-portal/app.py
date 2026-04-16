import streamlit as st
from pathlib import Path

st.set_page_config(
    page_title="GOL Customer Portal",
    page_icon="🟠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── inject CSS ──────────────────────────────────────────────────
css = Path("assets/style.css").read_text(encoding="utf-8")
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# ── Header ──────────────────────────────────────────────────────
st.markdown("""
<div style="display:flex; align-items:center; gap:16px; margin-bottom:0.5rem;">
  <div style="
    background:#F26322; border-radius:50%; width:54px; height:54px;
    display:flex; align-items:center; justify-content:center;
    font-weight:900; font-size:1.1rem; color:#fff; letter-spacing:-1px;
    box-shadow: 0 3px 10px rgba(242,99,34,0.35);
  ">GOL</div>
  <div>
    <div style="font-size:1.05rem; color:#6b7a99; font-weight:600; line-height:1.1;">Your next trip</div>
    <div style="font-size:1.05rem; color:#1a2744; font-weight:800; line-height:1.1;">starts here</div>
  </div>
  <div style="flex:1;"></div>
  <div style="color:#6b7a99; font-size:0.9rem; font-weight:600;">Customer Portal — Travelport GOL IBE</div>
</div>
<hr style="margin:0.75rem 0 1.25rem 0;">
""", unsafe_allow_html=True)

# ── Omnisearch ───────────────────────────────────────────────────
query = st.text_input(
    "",
    placeholder="🔍  Hledej akce, návody, nastavení… (např. 'jak přidat uživatele')",
    label_visibility="collapsed",
)

if query and query.strip():
    from core.search import search
    hits = search(query)
    if hits:
        for h in hits:
            st.markdown(f"**{h['title']}** · skóre {h['score']}  \n{h['snippet']}")
    else:
        st.info("Žádné výsledky. Zkus jiný dotaz nebo použij AI Pomocníka.")

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

# ── Navigation tiles ─────────────────────────────────────────────
st.markdown("### Kde chceš začít?")

tiles = [
    ("pages/1_AI_Assistant.py",  "💬", "AI Pomocník",    "Zeptej se na cokoliv"),
    ("pages/2_Walkthroughs.py",  "🗺️", "Průvodci",       "Krok za krokem"),
    ("pages/3_Agency_Health.py", "📊", "Agency Health",  "Přehled výkonu agentury"),
    ("pages/4_Changelog.py",     "🆕", "Co je nového",   "Release notes"),
]

cols = st.columns(4, gap="medium")
for col, (page, icon, label, sub) in zip(cols, tiles):
    with col:
        st.markdown(f"""
        <a class="nav-tile" href="{page}" target="_self">
          <span class="tile-icon">{icon}</span>
          <div class="tile-label">{label}</div>
          <div class="tile-sub">{sub}</div>
        </a>
        """, unsafe_allow_html=True)
