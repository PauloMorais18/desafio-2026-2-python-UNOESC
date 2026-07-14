"""Mocked Streamlit prototype for the academic assistant chat."""

from datetime import datetime
from time import sleep

import streamlit as st

from components.chat_bubble import render_chat_message
from components.header import render_header
from components.info_card import render_info_card
from components.message_input import render_message_input
from components.sidebar import render_sidebar

WELCOME_MESSAGE = "Olá! Como posso ajudá-lo hoje?"
MOCK_RESPONSE = (
    "Esta é uma resposta simulada. Futuramente esta resposta será gerada pelo "
    "Assistente Acadêmico através da API."
)


def reset_conversation() -> None:
    """Reset the in-memory conversation to the assistant welcome message."""
    st.session_state.messages = [
        {"role": "assistant", "content": WELCOME_MESSAGE, "time": current_time()}
    ]


def load_mock_history(conversation_name: str) -> None:
    """Load a visual-only conversation example into the current session."""
    st.session_state.messages = [
        {
            "role": "user",
            "content": f"Mensagem fictícia de {conversation_name}.",
            "time": "10:31",
        },
        {"role": "assistant", "content": MOCK_RESPONSE, "time": "10:32"},
    ]


def current_time() -> str:
    """Return a display-only timestamp for the mock conversation."""
    return datetime.now().strftime("%H:%M")


def initialize_state() -> None:
    """Create the transient state required by this local-only prototype."""
    if "messages" not in st.session_state:
        reset_conversation()


def main() -> None:
    """Render a navigable chat prototype without API or database access."""
    st.set_page_config(page_title="Assistente Acadêmico", page_icon="🎓", layout="wide")
    initialize_state()

    action = render_sidebar(st.session_state.get("active_conversation", "Conversa 1"))
    if action == "new":
        reset_conversation()
    elif action.startswith("history:"):
        conversation_name = action.removeprefix("history:")
        st.session_state.active_conversation = conversation_name
        load_mock_history(conversation_name)

    render_header()

    if action == "about":
        st.subheader("Sobre o UnoAssist")
        st.markdown(
            """
            <div class="about-card">
              <h3>UnoAssist · Assistente Acadêmico</h3>
              <p><strong>Tecnologias:</strong> Streamlit, FastAPI, PostgreSQL e LangChain.</p>
              <p><strong>Objetivo:</strong> facilitar dúvidas com base no conhecimento institucional.</p>
              <p><strong>Versão:</strong> 1.0</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    render_info_card()

    conversation = st.container(height=520, border=True)
    with conversation:
        for message in st.session_state.messages:
            render_chat_message(message["role"], message["content"], message["time"])
    st.markdown(
        '<p class="chat-hint">As respostas podem levar alguns segundos para serem geradas.</p>',
        unsafe_allow_html=True,
    )

    question = render_message_input()

    if question:
        st.session_state.messages.append(
            {"role": "user", "content": question, "time": current_time()}
        )
        with st.spinner("O assistente está preparando uma resposta..."):
            sleep(1)
        st.session_state.messages.append(
            {"role": "assistant", "content": MOCK_RESPONSE, "time": current_time()}
        )
        st.rerun()


if __name__ == "__main__":
    main()
