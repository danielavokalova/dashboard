import streamlit as st
from pathlib import Path
from core.ai_agent import get_response
from core.doc_loader import load_docs

st.set_page_config(page_title="AI Assistant – New Help Portal", page_icon="🤖", layout="wide")

_CSS = Path(__file__).parent.parent / "assets" / "style.css"
st.markdown(f"<style>{_CSS.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

st.markdown("### 🤖 AI Assistant")
st.caption("Ask anything about GOL IBE — I'll answer based on the documentation.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Type your question…"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking…"):
            docs = load_docs()
            response = get_response(prompt, docs, st.session_state.messages[:-1])
        st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})
