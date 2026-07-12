"""Message input component for the chat prototype."""

import streamlit as st


def render_message_input() -> str | None:
    """Render the mock message composer and return a submitted non-empty message."""
    with st.form("message_form", clear_on_submit=True):
        attachment, field, submit = st.columns([0.06, 0.76, 0.18], vertical_alignment="center")
        with attachment:
            st.markdown('<div class="attachment-icon">⌇</div>', unsafe_allow_html=True)
        with field:
            question = st.text_input(
                "Mensagem",
                placeholder="Digite sua dúvida acadêmica...",
                label_visibility="collapsed",
            )
        with submit:
            submitted = st.form_submit_button("➤ Enviar", use_container_width=True, type="primary")
    return question.strip() if submitted and question.strip() else None
