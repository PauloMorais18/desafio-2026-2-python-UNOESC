"""Mocked Streamlit prototype for the academic assistant chat."""

from time import sleep

import streamlit as st

from components.chat_bubble import render_chat_message
from components.header import render_header
from components.sidebar import render_sidebar

WELCOME_MESSAGE = "Olá! Como posso ajudá-lo hoje?"
MOCK_RESPONSE = (
    "Esta é uma resposta simulada. Futuramente esta resposta será gerada pelo "
    "Assistente Acadêmico através da API."
)


def reset_conversation() -> None:
    """Reset the in-memory conversation to the assistant welcome message."""
    st.session_state.messages = [{"role": "assistant", "content": WELCOME_MESSAGE}]


def load_mock_history(conversation_name: str) -> None:
    """Load a visual-only conversation example into the current session."""
    st.session_state.messages = [
        {"role": "user", "content": f"Mensagem fictícia de {conversation_name}."},
        {"role": "assistant", "content": MOCK_RESPONSE},
    ]


def initialize_state() -> None:
    """Create the transient state required by this local-only prototype."""
    if "messages" not in st.session_state:
        reset_conversation()


def main() -> None:
    """Render a navigable chat prototype without API or database access."""
    st.set_page_config(page_title="Assistente Acadêmico", page_icon="🎓", layout="wide")
    initialize_state()

    action = render_sidebar()
    if action == "new":
        reset_conversation()
    elif action.startswith("history:"):
        load_mock_history(action.removeprefix("history:"))

    render_header()

    if action == "about":
        st.subheader("Sobre o projeto")
        st.markdown(
            """
            <div class="about-card">
              <h3>Assistente Acadêmico</h3>
              <p><strong>Tecnologias:</strong> Streamlit, FastAPI, PostgreSQL e LangChain.</p>
              <p><strong>Objetivo:</strong> facilitar dúvidas com base no conhecimento institucional.</p>
              <p><strong>Versão:</strong> 1.0</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    st.caption("O assistente responde apenas perguntas presentes na base de conhecimento.")
    st.divider()

    for message in st.session_state.messages:
        render_chat_message(message["role"], message["content"])

    with st.form("message_form", clear_on_submit=True):
        question = st.text_input(
            "Mensagem",
            placeholder="Digite sua dúvida acadêmica...",
            label_visibility="collapsed",
        )
        submitted = st.form_submit_button("Enviar", use_container_width=True, type="primary")

    if submitted and question.strip():
        st.session_state.messages.append({"role": "user", "content": question.strip()})
        render_chat_message("user", question.strip())
        with st.spinner("O assistente está preparando uma resposta..."):
            sleep(1)
        st.session_state.messages.append({"role": "assistant", "content": MOCK_RESPONSE})
        render_chat_message("assistant", MOCK_RESPONSE)


if __name__ == "__main__":
    main()
