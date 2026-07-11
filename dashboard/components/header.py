"""Header component for the dashboard prototype."""

import streamlit as st


def render_header() -> None:
    """Render the product title and version consistently."""
    st.markdown(
        """
        <style>
          .stApp { background: #f8fafc; color: #172033; }
          .app-header { display: flex; align-items: center; justify-content: space-between;
            padding: 0.6rem 0 1.5rem; }
          .app-header h1 { margin: 0; color: #172033; font-size: 2rem; letter-spacing: -0.04em; }
          .app-header p { margin: 0.35rem 0 0; color: #64748b; }
          .app-header span { color: #475569; background: #eaf2ff; border-radius: 999px;
            padding: 0.35rem 0.75rem; font-size: 0.85rem; }
          .stat-card { min-height: 132px; background: #fff; border: 1px solid #e2e8f0;
            border-radius: 14px; padding: 1rem 1.1rem; box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04); }
          .stat-card p { color: #64748b; font-size: 0.88rem; margin: 0; }
          .stat-card h2 { color: #172033; margin: 0.55rem 0; font-size: 1.75rem; }
          .stat-card span { color: #2563eb; font-size: 0.8rem; }
        </style>
        <div class="app-header">
          <div>
            <h1>Assistente Acadêmico</h1>
            <p>Painel administrativo</p>
          </div>
          <span>Versão 1.0</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
