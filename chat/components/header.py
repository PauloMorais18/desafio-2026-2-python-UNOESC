"""Header component for the chat application."""

import streamlit as st


def render_header() -> None:
    """Render the product title and version consistently."""
    st.markdown(
        """
        <style>
          .stApp { background: #f8fafc; color: #172033; }
          [data-testid="stSidebar"] { background: #ffffff; border-right: 1px solid #e5e7eb; }
          .app-header { display: flex; align-items: center; justify-content: space-between;
            padding: 0.6rem 0 1.5rem; }
          .app-header h1 { margin: 0; color: #172033; font-size: 2rem; letter-spacing: -0.04em; }
          .app-header p { margin: 0.35rem 0 0; color: #64748b; }
          .app-header span { color: #475569; background: #eaf2ff; border-radius: 999px;
            padding: 0.35rem 0.75rem; font-size: 0.85rem; }
          .about-card { background: #fff; border: 1px solid #e2e8f0; border-radius: 14px;
            padding: 1.4rem 1.6rem; box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04); }
          .about-card h3 { margin-top: 0; }
          .about-card p { color: #475569; }
          [data-testid="stChatMessage"] { background: #fff; border: 1px solid #e5e7eb;
            border-radius: 12px; padding: 0.5rem; }
        </style>
        <div class="app-header">
          <div>
            <h1>Assistente Acadêmico</h1>
            <p>Tire dúvidas utilizando a base de conhecimento da instituição.</p>
          </div>
          <span>Versão 1.0</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
