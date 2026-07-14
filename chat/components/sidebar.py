"""Sidebar navigation component for the chat prototype."""

import streamlit as st


def render_sidebar(active_conversation: str) -> str:
    """Render mock navigation and return the selected local action."""
    with st.sidebar:
        st.markdown(
            """
            <div class="brand">
              <div class="brand-mark">◢</div>
              <div><b>UnoAssist</b><br><span>Assistente Acadêmico</span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("＋  Novo Chat", use_container_width=True, type="primary"):
            return "new"

        st.markdown('<p class="sidebar-label">HISTÓRICO</p>', unsafe_allow_html=True)
        for conversation in ("Conversa 1", "Conversa 2", "Conversa 3", "Conversa 4", "Conversa 5"):
            if conversation == active_conversation:
                st.markdown(
                    f'<div class="conversation-active">◯<span>{conversation}</span></div>',
                    unsafe_allow_html=True,
                )
                continue
            if st.button(
                f"◯  {conversation}",
                use_container_width=True,
                key=f"history_{conversation}",
                type="secondary",
            ):
                return f"history:{conversation}"

        st.divider()
        st.markdown('<p class="sidebar-label">OUTRAS OPÇÕES</p>', unsafe_allow_html=True)
        if st.button("ⓘ  Sobre o Assistente", use_container_width=True):
            return "about"
        st.button("⚙  Configurações", use_container_width=True, disabled=True)

        st.markdown('<div class="sidebar-bottom">', unsafe_allow_html=True)
        st.divider()
        st.button("⇥  Sair", use_container_width=True, disabled=True)
        st.markdown("</div>", unsafe_allow_html=True)

    return "chat"
