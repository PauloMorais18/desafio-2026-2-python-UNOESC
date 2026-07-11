"""Message component for the chat prototype."""

import streamlit as st


def render_chat_message(role: str, content: str) -> None:
    """Render one message using Streamlit's accessible chat presentation."""
    avatar = "🎓" if role == "assistant" else "👤"
    with st.chat_message(role, avatar=avatar):
        st.write(content)
