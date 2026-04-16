"""Shared UI helpers — GOL theme loader."""
from pathlib import Path
import streamlit as st

_CSS_PATH = Path(__file__).parent.parent / "assets" / "style.css"


def apply_theme():
    """Inject GOL CSS into the current page."""
    css = _CSS_PATH.read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def gol_header(subtitle: str = ""):
    """Render the GOL logo header strip."""
    sub_html = f'<div style="color:#6b7a99;font-size:0.9rem;font-weight:600;">{subtitle}</div>' if subtitle else ""
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:14px;margin-bottom:0.5rem;">
      <div style="
        background:#F26322;border-radius:50%;width:46px;height:46px;
        display:flex;align-items:center;justify-content:center;
        font-weight:900;font-size:0.95rem;color:#fff;letter-spacing:-1px;
        box-shadow:0 3px 10px rgba(242,99,34,0.35);
      ">GOL</div>
      <div>
        <div style="font-size:0.9rem;color:#6b7a99;font-weight:600;line-height:1.1;">Customer Portal</div>
        <div style="font-size:1rem;color:#1a2744;font-weight:800;line-height:1.1;">Travelport GOL IBE</div>
      </div>
      <div style="flex:1;"></div>
      {sub_html}
    </div>
    <hr style="margin:0.6rem 0 1rem 0;">
    """, unsafe_allow_html=True)
