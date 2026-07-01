import streamlit as st
from chat_agent import run_agent_graph
import os
from config import MEMORY_FILE
from utils import *


st.set_page_config(page_title="Agent Wiki TUIASI", page_icon="🤖")

if "memory_initialized" not in st.session_state:
    clear_memory_on_start()
    st.session_state.memory_initialized = True

#st.title("🤖 Agent Wiki TUIASI")

if "messages" not in st.session_state:
    st.session_state.messages = []

# afișează istoric chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# input user
user_input = st.chat_input("Write your question...")

if user_input:
    # afișează user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # rulează agentul
    with st.chat_message("assistant"):
        with st.spinner("Thinking... "):
            response = run_agent_graph(user_input)

            # IMPORTANT: modificăm funcția să RETURNeze răspunsul
            st.markdown(response)

            st.session_state.messages.append(
                {"role": "assistant", "content": response}
            )
