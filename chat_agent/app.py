import streamlit as st
from chat_agent import run_agent_graph
from utils import *


st.set_page_config(page_title="Agent Wiki TUIASI", page_icon="🤖")

if "memory" not in st.session_state:
    st.session_state.memory = []

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Write your question...")

if user_input:
    # afișează user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # rulează agentul
    with st.chat_message("assistant"):
        with st.spinner("Thinking... "):
            response, st.session_state.memory = run_agent_graph(
                user_input,
                st.session_state.memory
            )

            st.markdown(response)

            st.session_state.messages.append(
                {"role": "assistant", "content": response}
            )
