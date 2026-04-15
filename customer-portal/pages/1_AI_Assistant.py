"""
Page 1 – AI Assistant (L0 support layer)
Chat interface powered by Claude. Context injected from the knowledge base.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

st.set_page_config(
    page_title="AI Assistant · New Help Portal",
    page_icon="🤖",
    layout="centered",
)

st.title("🤖 AI Assistant")
st.caption(
    "Ask me anything about the GOL IBE Admin Console. "
    "I'll answer instantly using the official documentation."
)

# ── Check API key ─────────────────────────────────────────────────────────────
import os
api_key = os.getenv("ANTHROPIC_API_KEY", "")
if not api_key:
    st.warning(
        "**AI Assistant is not configured yet.**\n\n"
        "Add your `ANTHROPIC_API_KEY` to the `.env` file in the `customer-portal/` folder.\n\n"
        "See `.env.example` for instructions.",
        icon="⚠️",
    )
    st.info("You can still use 🗺️ Guided Walkthroughs and 📊 Agency Health Check without the API key.")
    st.stop()

from core.ai_agent import ask_agent

# ── Session state ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "assistant",
        "content": (
            "Hi! I'm your GOL IBE assistant. 👋\n\n"
            "I can help you with:\n"
            "- **Reservations** – create, modify, cancel, ticket\n"
            "- **Users** – manage agents and permissions\n"
            "- **Prices & markup** – fares, fees and surcharges\n"
            "- **Settings** – agency setup, connectors, notifications\n\n"
            "What can I help you with today?"
        ),
    })

# ── Render history ────────────────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── Input ─────────────────────────────────────────────────────────────────────
if prompt := st.chat_input("Type your question…"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking…"):
            try:
                history = st.session_state.messages[:-1]
                answer = ask_agent(prompt, history=history)
            except Exception as e:
                answer = (
                    "Sorry, something went wrong. Please try again.\n\n"
                    f"`{e}`"
                )
        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})

# ── Footer ────────────────────────────────────────────────────────────────────
st.divider()
col1, col2 = st.columns(2)
with col1:
    st.markdown("**Still stuck?**")
with col2:
    if st.button("💬  Talk to a human agent", use_container_width=True):
        st.info("Forwarding to support with your full conversation context…")

if st.button("🗑️  Clear conversation", type="secondary"):
    st.session_state.messages = []
    st.rerun()
