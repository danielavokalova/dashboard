import streamlit as st
from core.ai_agent import get_response
from core.doc_loader import load_docs
from core.ui import apply_theme, gol_header

st.set_page_config(page_title="AI Pomocník – GOL", page_icon="💬", layout="wide")
apply_theme()
gol_header("AI Pomocník")

st.markdown("### 💬 AI Pomocník")
st.caption("Zeptej se na cokoliv ohledně systému — odpovím v kontextu dokumentace.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Napiš dotaz…"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Přemýšlím…"):
            docs = load_docs()
            response = get_response(prompt, docs, st.session_state.messages[:-1])
        st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})
