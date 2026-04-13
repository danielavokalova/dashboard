"""
Page 1 – AI Assistant
─────────────────────
Chat interface powered by Claude (Anthropic).
The agent has access to the GOL IBE knowledge base and answers in plain language.

L0 support layer: fully automated, instant, context-aware.
If the agent cannot resolve the issue, it hands off to L2 (human support).
"""

import streamlit as st
from dotenv import load_dotenv
from core.ai_agent import ask_agent

load_dotenv()

st.set_page_config(page_title="AI Assistant · GOL IBE Help", page_icon="🤖", layout="centered")

# ── Header ────────────────────────────────────────────────────────────────────
st.title("🤖 AI Assistant")
st.caption(
    "Ask me anything about the GOL IBE Admin Console. "
    "I'll answer in seconds using the official documentation."
)

# ── Session state ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Greeting message
    st.session_state.messages.append({
        "role": "assistant",
        "content": (
            "Hi! I'm your GOL IBE assistant. 👋\n\n"
            "I can help you with:\n"
            "- **Reservations** – create, modify, cancel bookings\n"
            "- **Users** – manage agents and permissions\n"
            "- **Prices & markup** – configure fares and surcharges\n"
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
    # Show user message immediately
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get AI response
    with st.chat_message("assistant"):
        with st.spinner("Thinking…"):
            try:
                # Pass history without the latest user message (it's added inside ask_agent)
                history = st.session_state.messages[:-1]
                answer = ask_agent(prompt, history=history)
            except EnvironmentError as e:
                answer = (
                    f"⚠️ **Configuration error:** {e}\n\n"
                    "Please set up your `.env` file (see `.env.example`)."
                )
            except Exception as e:
                answer = (
                    "Sorry, I ran into an issue. Please try again or "
                    f"[contact support](mailto:support@golibe.com).\n\n`{e}`"
                )
        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})

# ── Escalation footer ─────────────────────────────────────────────────────────
st.divider()
col1, col2 = st.columns(2)
with col1:
    st.markdown("**Still stuck?**")
with col2:
    if st.button("💬  Talk to a human agent", use_container_width=True):
        # TODO: open live-chat widget or Zendesk ticket with conversation context
        st.info(
            "Handing off to the support team…\n\n"
            "Your conversation history will be shared so the agent has full context."
        )

if st.button("🗑️  Clear conversation", type="secondary"):
    st.session_state.messages = []
    st.rerun()
