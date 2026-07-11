"""Sidebar navigation component for the chat prototype."""

import streamlit as st


def render_sidebar() -> str:
    """Render mock navigation and return the selected local action."""
    with st.sidebar:
        st.markdown("## 🎓 Assistente")
        if st.button("＋ Novo Chat", use_container_width=True, type="primary"):
            return "new"

        st.markdown("### Histórico")
        for conversation in ("Conversa 1", "Conversa 2", "Conversa 3"):
            if st.button(conversation, use_container_width=True, key=f"history_{conversation}"):
                return f"history:{conversation}"

        st.divider()
        if st.button("Sobre", use_container_width=True):
            return "about"

    return "chat"
