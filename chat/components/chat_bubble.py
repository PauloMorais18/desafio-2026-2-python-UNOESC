"""Message component for the chat prototype."""

from html import escape

import streamlit as st


def render_chat_message(role: str, content: str, timestamp: str) -> None:
    """Render one visual chat bubble with avatar, content, and timestamp."""
    is_user = role == "user"
    avatar_class = "user-avatar" if is_user else ""
    avatar = "◉" if is_user else "✦"
    safe_content = escape(content)
    st.markdown(
        f"""
        <div class="message-row {"user" if is_user else "assistant"}">
          {"" if is_user else f'<div class="message-avatar {avatar_class}">{avatar}</div>'}
          <div class="message-bubble">{safe_content}<span class="message-time">{escape(timestamp)}</span></div>
          {f'<div class="message-avatar {avatar_class}">{avatar}</div>' if is_user else ""}
        </div>
        """,
        unsafe_allow_html=True,
    )
