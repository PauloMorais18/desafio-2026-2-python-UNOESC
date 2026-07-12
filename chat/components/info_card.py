"""Informational card component for the chat prototype."""

import streamlit as st


def render_info_card() -> None:
    """Render a calm informational notice about the mock assistant scope."""
    st.markdown(
        """
        <div class="info-card">
          <div class="info-icon">ⓘ</div>
          <p>O assistente responde apenas perguntas presentes na base de conhecimento cadastrada pela instituição.<br>
          Caso não encontre informações suficientes, ele informará isso ao usuário.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
